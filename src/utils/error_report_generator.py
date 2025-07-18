"""
오류 수집 및 기록 시스템
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import traceback
import sys
from collections import Counter

from logger.app_logger import get_logger

class ErrorCollector:
    """오류 수집 및 기록"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.error_dir = Path.home() / '.excel_macro_automation' / 'collected_errors'
        self.error_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_errors(self, days: int = 7) -> List[Dict[str, Any]]:
        """오류 수집 메인 메서드"""
        errors = self._collect_recent_errors(days)
        self._save_collected_errors(errors, days)
        return errors
    
    def _collect_recent_errors(self, days: int) -> List[Dict[str, Any]]:
        """최근 오류 수집"""
        errors = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # 1. 오류 복구 히스토리에서 수집
        recovery_history = self._load_recovery_history()
        for record in recovery_history:
            try:
                timestamp = datetime.fromisoformat(record['timestamp'])
                if timestamp > cutoff_date and not record.get('success', True):
                    errors.append({
                        'timestamp': timestamp,
                        'type': record.get('error_type', 'Unknown'),
                        'message': record.get('error_msg', ''),
                        'source': 'recovery_system',
                        'pattern': record.get('pattern', ''),
                        'context': {}
                    })
            except:
                pass
        
        # 2. 실행 로그에서 수집
        execution_errors = self._collect_from_execution_logs(cutoff_date)
        errors.extend(execution_errors)
        
        # 3. 애플리케이션 로그에서 수집
        app_errors = self._collect_from_app_logs(cutoff_date)
        errors.extend(app_errors)
        
        # 시간순 정렬
        errors.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return errors
    
    def _load_recovery_history(self) -> List[Dict]:
        """복구 히스토리 로드"""
        history_file = Path.home() / '.excel_macro_automation' / 'error_recovery_history.json'
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _collect_from_execution_logs(self, cutoff_date: datetime) -> List[Dict]:
        """실행 로그에서 오류 수집"""
        errors = []
        log_dir = Path.home() / '.excel_macro_automation' / 'execution_logs'
        
        if log_dir.exists():
            for log_file in log_dir.glob('*.csv'):
                try:
                    # CSV 파일에서 오류 찾기
                    import csv
                    with open(log_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row.get('status') == 'FAILED':
                                timestamp = datetime.fromisoformat(row.get('timestamp', ''))
                                if timestamp > cutoff_date:
                                    errors.append({
                                        'timestamp': timestamp,
                                        'type': 'ExecutionError',
                                        'message': row.get('error', ''),
                                        'source': 'execution_log',
                                        'context': {
                                            'step': row.get('step_name', ''),
                                            'row': row.get('row_index', '')
                                        }
                                    })
                except:
                    pass
                    
        return errors
    
    def _collect_from_app_logs(self, cutoff_date: datetime) -> List[Dict]:
        """애플리케이션 로그에서 오류 수집"""
        errors = []
        log_dir = Path.home() / '.excel_macro_automation' / 'logs'
        
        if log_dir.exists():
            for log_file in log_dir.glob('*.log'):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if 'ERROR' in line:
                                # 로그 라인 파싱
                                parts = line.split(' - ', 2)
                                if len(parts) >= 3:
                                    try:
                                        timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S,%f')
                                        if timestamp > cutoff_date:
                                            errors.append({
                                                'timestamp': timestamp,
                                                'type': 'ApplicationError',
                                                'message': parts[2].strip(),
                                                'source': 'app_log',
                                                'context': {}
                                            })
                                    except:
                                        pass
                except:
                    pass
                    
        return errors
    
    def _save_collected_errors(self, errors: List[Dict[str, Any]], days: int = 7):
        """수집된 오류를 파일로 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        error_file = self.error_dir / f'errors_{timestamp}.json'
        
        # 날짜 객체를 문자열로 변환
        serializable_errors = []
        for error in errors:
            error_copy = error.copy()
            if isinstance(error_copy.get('timestamp'), datetime):
                error_copy['timestamp'] = error_copy['timestamp'].isoformat()
            serializable_errors.append(error_copy)
        
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_errors, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"오류 {len(errors)}개를 {error_file}에 저장")
        
        # 최신 오류 파일 링크 생성
        latest_link = self.error_dir / 'latest_errors.json'
        if latest_link.exists():
            latest_link.unlink()
        
        with open(latest_link, 'w', encoding='utf-8') as f:
            json.dump({
                'file': error_file.name,
                'timestamp': timestamp,
                'count': len(errors),
                'days_collected': days
            }, f, ensure_ascii=False, indent=2)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """오류 요약 통계 반환"""
        errors = self.collect_errors(7)  # 최근 7일
        
        summary = {
            'total_errors': len(errors),
            'error_types': {},
            'sources': {},
            'recent_errors': []
        }
        
        # 유형별 집계
        for error in errors:
            error_type = error.get('type', 'Unknown')
            summary['error_types'][error_type] = summary['error_types'].get(error_type, 0) + 1
            
            source = error.get('source', 'unknown')
            summary['sources'][source] = summary['sources'].get(source, 0) + 1
        
        # 최근 5개 오류
        summary['recent_errors'] = errors[:5]
        
        return summary
    
    def get_latest_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """최신 오류 파일에서 지정된 개수만큼 오류 반환"""
        latest_link = self.error_dir / 'latest_errors.json'
        
        if latest_link.exists():
            try:
                with open(latest_link, 'r', encoding='utf-8') as f:
                    link_info = json.load(f)
                    
                error_file = self.error_dir / link_info['file']
                if error_file.exists():
                    with open(error_file, 'r', encoding='utf-8') as f:
                        errors = json.load(f)
                        return errors[:count]
            except:
                pass
                
        return []
    
    def clear_old_errors(self, days: int = 30):
        """오래된 오류 파일 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned = 0
        
        for error_file in self.error_dir.glob('errors_*.json'):
            try:
                # 파일명에서 날짜 추출
                date_str = error_file.stem.split('_')[1]
                file_date = datetime.strptime(date_str[:8], '%Y%m%d')
                
                if file_date < cutoff_date:
                    error_file.unlink()
                    cleaned += 1
            except:
                pass
                
        if cleaned > 0:
            self.logger.info(f"{cleaned}개의 오래된 오류 파일 정리")

# 사용 예시 함수
def collect_and_save_errors(days: int = 7) -> int:
    """오류 수집 및 저장 헬퍼 함수"""
    collector = ErrorCollector()
    errors = collector.collect_errors(days)
    return len(errors)

def get_recent_error_summary() -> Dict[str, Any]:
    """최근 오류 요약 반환"""
    collector = ErrorCollector()
    return collector.get_error_summary()