"""
백그라운드 모니터링 시스템
애플리케이션 상태를 실시간으로 감시하고 문제를 사전에 감지/해결
"""

import threading
import time
import psutil
import os
import sys
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import json

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from logger.app_logger import get_logger
from utils.error_recovery import get_recovery_manager
from utils.self_diagnosis import SelfDiagnosis

class MonitoringRule:
    """모니터링 규칙"""
    def __init__(self, name: str, check_func: Callable, 
                 threshold: Any, action_func: Callable = None,
                 check_interval: int = 30):
        self.name = name
        self.check_func = check_func
        self.threshold = threshold
        self.action_func = action_func
        self.check_interval = check_interval
        self.last_check = datetime.now()
        self.violation_count = 0
        self.last_value = None
        
class SystemMetrics:
    """시스템 메트릭 수집"""
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.cpu_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.disk_history = deque(maxlen=history_size)
        self.thread_count_history = deque(maxlen=history_size)
        
    def collect(self):
        """현재 메트릭 수집"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'disk_percent': psutil.disk_usage('/').percent,
            'disk_free_gb': psutil.disk_usage('/').free / 1024 / 1024 / 1024,
            'thread_count': threading.active_count(),
            'process_count': len(psutil.pids())
        }
        
        # 히스토리에 추가
        self.cpu_history.append(metrics['cpu_percent'])
        self.memory_history.append(metrics['memory_percent'])
        self.disk_history.append(metrics['disk_percent'])
        self.thread_count_history.append(metrics['thread_count'])
        
        return metrics
        
    def get_average(self, metric_name: str, window: int = 10) -> float:
        """최근 N개 샘플의 평균"""
        history_map = {
            'cpu': self.cpu_history,
            'memory': self.memory_history,
            'disk': self.disk_history,
            'threads': self.thread_count_history
        }
        
        history = history_map.get(metric_name, [])
        if not history:
            return 0
            
        recent = list(history)[-window:]
        return sum(recent) / len(recent) if recent else 0

class BackgroundMonitor(QObject):
    """백그라운드 모니터링 시스템"""
    
    # 시그널
    alert_signal = pyqtSignal(str, str)  # (규칙명, 메시지)
    metrics_updated = pyqtSignal(dict)   # 메트릭 업데이트
    health_status_changed = pyqtSignal(str)  # 상태 변경
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.recovery_manager = get_recovery_manager()
        self.diagnosis = SelfDiagnosis()
        
        self.is_running = False
        self.rules: List[MonitoringRule] = []
        self.metrics = SystemMetrics()
        self.health_status = "정상"
        self.alert_history = deque(maxlen=50)
        
        # 모니터링 타이머
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._run_checks)
        
        # 초기 규칙 설정
        self._setup_default_rules()
        
    def _setup_default_rules(self):
        """기본 모니터링 규칙 설정"""
        # CPU 사용률 모니터링
        self.add_rule(
            "high_cpu",
            lambda: self.metrics.get_average('cpu', 5),
            80.0,  # 80% 이상
            self._handle_high_cpu,
            check_interval=10
        )
        
        # 메모리 사용률 모니터링
        self.add_rule(
            "high_memory",
            lambda: self.metrics.get_average('memory', 5),
            85.0,  # 85% 이상
            self._handle_high_memory,
            check_interval=15
        )
        
        # 디스크 공간 모니터링
        self.add_rule(
            "low_disk",
            lambda: psutil.disk_usage('/').percent,
            90.0,  # 90% 이상 사용
            self._handle_low_disk,
            check_interval=60
        )
        
        # 스레드 수 모니터링
        self.add_rule(
            "thread_leak",
            lambda: threading.active_count(),
            100,  # 100개 이상
            self._handle_thread_leak,
            check_interval=30
        )
        
        # 로그 파일 크기 모니터링
        self.add_rule(
            "log_size",
            self._check_log_size,
            100,  # 100MB 이상
            self._handle_large_logs,
            check_interval=300  # 5분마다
        )
        
        # 임시 파일 모니터링
        self.add_rule(
            "temp_files",
            self._count_temp_files,
            50,  # 50개 이상
            self._clean_temp_files,
            check_interval=600  # 10분마다
        )
        
    def add_rule(self, name: str, check_func: Callable, 
                 threshold: Any, action_func: Callable = None,
                 check_interval: int = 30):
        """모니터링 규칙 추가"""
        rule = MonitoringRule(name, check_func, threshold, action_func, check_interval)
        self.rules.append(rule)
        self.logger.info(f"모니터링 규칙 추가: {name}")
        
    def start(self):
        """모니터링 시작"""
        if self.is_running:
            return
            
        self.is_running = True
        self.logger.info("백그라운드 모니터링 시작")
        
        # 타이머 시작 (5초마다 체크)
        self.monitor_timer.start(5000)
        
        # 초기 메트릭 수집
        self._collect_metrics()
        
    def stop(self):
        """모니터링 중지"""
        self.is_running = False
        self.monitor_timer.stop()
        self.logger.info("백그라운드 모니터링 중지")
        
        # 최종 리포트 저장
        self._save_report()
        
    def _run_checks(self):
        """모든 체크 실행"""
        if not self.is_running:
            return
            
        try:
            # 메트릭 수집
            current_metrics = self._collect_metrics()
            
            # 규칙 검사
            alerts = []
            for rule in self.rules:
                # 체크 간격 확인
                elapsed = (datetime.now() - rule.last_check).total_seconds()
                if elapsed < rule.check_interval:
                    continue
                    
                rule.last_check = datetime.now()
                
                try:
                    # 체크 실행
                    value = rule.check_func()
                    rule.last_value = value
                    
                    # 임계값 위반 체크
                    violated = False
                    if isinstance(rule.threshold, (int, float)):
                        violated = value > rule.threshold
                    elif callable(rule.threshold):
                        violated = rule.threshold(value)
                        
                    if violated:
                        rule.violation_count += 1
                        self.logger.warning(f"규칙 위반: {rule.name} (값: {value}, 임계값: {rule.threshold})")
                        
                        # 액션 실행
                        if rule.action_func and rule.violation_count >= 3:
                            self.logger.info(f"복구 액션 실행: {rule.name}")
                            rule.action_func()
                            rule.violation_count = 0
                            
                        alerts.append((rule.name, f"{rule.name}: {value}"))
                    else:
                        rule.violation_count = 0
                        
                except Exception as e:
                    self.logger.error(f"규칙 체크 실패 ({rule.name}): {e}")
                    
            # 상태 업데이트
            self._update_health_status(alerts)
            
            # 시그널 발송
            self.metrics_updated.emit(current_metrics)
            
            for alert in alerts:
                self.alert_signal.emit(*alert)
                self._add_alert(*alert)
                
        except Exception as e:
            self.logger.error(f"모니터링 체크 중 오류: {e}")
            
    def _collect_metrics(self) -> dict:
        """메트릭 수집"""
        try:
            return self.metrics.collect()
        except Exception as e:
            self.logger.error(f"메트릭 수집 실패: {e}")
            return {}
            
    def _update_health_status(self, alerts: List[tuple]):
        """건강 상태 업데이트"""
        old_status = self.health_status
        
        if not alerts:
            self.health_status = "정상"
        elif len(alerts) < 3:
            self.health_status = "주의"
        else:
            self.health_status = "위험"
            
        if old_status != self.health_status:
            self.health_status_changed.emit(self.health_status)
            self.logger.info(f"시스템 상태 변경: {old_status} -> {self.health_status}")
            
    def _add_alert(self, rule_name: str, message: str):
        """알림 기록 추가"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'rule': rule_name,
            'message': message
        }
        self.alert_history.append(alert)
        
    # 체크 함수들
    def _check_log_size(self) -> float:
        """로그 파일 크기 체크 (MB)"""
        log_dir = Path.home() / '.excel_macro_automation' / 'logs'
        if not log_dir.exists():
            return 0
            
        total_size = 0
        for log_file in log_dir.glob('*.log*'):
            total_size += log_file.stat().st_size
            
        return total_size / 1024 / 1024  # MB
        
    def _count_temp_files(self) -> int:
        """임시 파일 개수"""
        temp_dir = Path(os.environ.get('TEMP', '/tmp'))
        count = 0
        
        try:
            for f in temp_dir.glob('tmp*'):
                if f.is_file():
                    count += 1
        except:
            pass
            
        return count
        
    # 액션 함수들
    def _handle_high_cpu(self):
        """높은 CPU 사용률 처리"""
        self.logger.warning("높은 CPU 사용률 감지, 가비지 컬렉션 실행")
        import gc
        gc.collect()
        
    def _handle_high_memory(self):
        """높은 메모리 사용률 처리"""
        self.logger.warning("높은 메모리 사용률 감지, 메모리 정리 시도")
        import gc
        gc.collect()
        
        # 큰 객체 정리
        gc.collect(2)
        
    def _handle_low_disk(self):
        """디스크 공간 부족 처리"""
        self.logger.warning("디스크 공간 부족, 임시 파일 정리")
        self._clean_temp_files()
        self._clean_old_logs()
        
    def _handle_thread_leak(self):
        """스레드 누수 처리"""
        self.logger.warning(f"과도한 스레드 감지: {threading.active_count()}개")
        # 스레드 목록 로깅
        for thread in threading.enumerate():
            self.logger.debug(f"  - {thread.name}: {thread.is_alive()}")
            
    def _handle_large_logs(self):
        """큰 로그 파일 처리"""
        self.logger.info("로그 파일 정리 시작")
        self._clean_old_logs()
        
    def _clean_temp_files(self):
        """임시 파일 정리"""
        temp_dir = Path(os.environ.get('TEMP', '/tmp'))
        cleaned = 0
        
        try:
            for f in temp_dir.glob('tmp*'):
                if f.is_file():
                    try:
                        # 1일 이상 된 파일만 삭제
                        age = datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)
                        if age > timedelta(days=1):
                            f.unlink()
                            cleaned += 1
                    except:
                        pass
                        
            self.logger.info(f"임시 파일 {cleaned}개 정리됨")
        except Exception as e:
            self.logger.error(f"임시 파일 정리 실패: {e}")
            
    def _clean_old_logs(self):
        """오래된 로그 파일 정리"""
        log_dir = Path.home() / '.excel_macro_automation' / 'logs'
        if not log_dir.exists():
            return
            
        cleaned = 0
        try:
            for log_file in log_dir.glob('*.log.*'):
                try:
                    # 7일 이상 된 로그 파일 삭제
                    age = datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)
                    if age > timedelta(days=7):
                        log_file.unlink()
                        cleaned += 1
                except:
                    pass
                    
            self.logger.info(f"오래된 로그 파일 {cleaned}개 정리됨")
        except Exception as e:
            self.logger.error(f"로그 정리 실패: {e}")
            
    def get_status_report(self) -> dict:
        """현재 상태 리포트"""
        report = {
            'health_status': self.health_status,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'cpu_avg': self.metrics.get_average('cpu', 10),
                'memory_avg': self.metrics.get_average('memory', 10),
                'disk_usage': psutil.disk_usage('/').percent,
                'thread_count': threading.active_count()
            },
            'rules': [
                {
                    'name': rule.name,
                    'last_value': rule.last_value,
                    'threshold': rule.threshold,
                    'violations': rule.violation_count
                }
                for rule in self.rules
            ],
            'recent_alerts': list(self.alert_history)[-10:]
        }
        
        return report
        
    def _save_report(self):
        """리포트 저장"""
        try:
            report_file = Path.home() / '.excel_macro_automation' / 'monitor_report.json'
            report_file.parent.mkdir(exist_ok=True)
            
            report = self.get_status_report()
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"리포트 저장 실패: {e}")

# 전역 인스턴스
_monitor = None

def get_monitor() -> BackgroundMonitor:
    """모니터 인스턴스 반환"""
    global _monitor
    if _monitor is None:
        _monitor = BackgroundMonitor()
    return _monitor