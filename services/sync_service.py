# services/sync_service.py
"""
Optimized data synchronization service with caching
"""
import asyncio
from typing import Dict, List
from memory.db import (
    CacheManager, get_user_credentials, update_sync_status,
    update_user_progress, update_problem_status, save_weakness_analysis
)
from tracker.tracker import call_mcp
import json

class SyncService:
    """High-performance sync service with intelligent caching"""
    
    @staticmethod
    async def sync_leetcode_data(user_id: int, force_refresh: bool = False) -> Dict:
        """
        Sync LeetCode data with intelligent caching
        - Uses cache if available and not force_refresh
        - Fetches from API if cache miss or force_refresh
        - Updates database and cache
        """
        cache_key = f"leetcode_data_{user_id}"
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = CacheManager.get(cache_key, user_id)
            if cached_data:
                return {"success": True, "data": cached_data, "source": "cache"}
        
        # Get credentials
        creds = get_user_credentials(user_id, 'leetcode')
        if not creds:
            return {"success": False, "error": "LeetCode credentials not found"}
        
        try:
            # Fetch from LeetCode API
            result = call_mcp("leetcode_stats", {
                "username": creds['username'],
                "session_cookie": creds['session_cookie']
            })
            
            if result.get('errors'):
                update_sync_status(user_id, 'leetcode', 'failed')
                return {"success": False, "error": result['errors']}
            
            # Extract and process data
            data = result.get('data', {})
            matched_user = data.get('matchedUser', {})
            submit_stats = matched_user.get('submitStats', {})
            ac_submissions = submit_stats.get('acSubmissionNum', [])
            
            # Parse stats
            stats = {entry['difficulty']: entry['count'] for entry in ac_submissions}
            recent_submissions = data.get('recentAcSubmissionList', [])
            
            processed_data = {
                'total_solved': stats.get('All', 0),
                'easy_solved': stats.get('Easy', 0),
                'medium_solved': stats.get('Medium', 0),
                'hard_solved': stats.get('Hard', 0),
                'recent_submissions': recent_submissions[:20],
                'last_synced': str(asyncio.get_event_loop().time())
            }
            
            # Update cache (15 minutes TTL)
            CacheManager.set(cache_key, processed_data, ttl_seconds=900, user_id=user_id)
            
            # Update sync status
            update_sync_status(user_id, 'leetcode', 'success')
            
            return {"success": True, "data": processed_data, "source": "api"}
            
        except Exception as e:
            update_sync_status(user_id, 'leetcode', 'failed')
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def sync_github_data(user_id: int, force_refresh: bool = False) -> Dict:
        """Sync GitHub data with caching"""
        cache_key = f"github_data_{user_id}"
        
        if not force_refresh:
            cached_data = CacheManager.get(cache_key, user_id)
            if cached_data:
                return {"success": True, "data": cached_data, "source": "cache"}
        
        creds = get_user_credentials(user_id, 'github')
        if not creds:
            return {"success": False, "error": "GitHub credentials not found"}
        
        try:
            result = call_mcp("list_repos", {
                "username": creds['username'],
                "token": creds['encrypted_token']
            })
            
            if not result.get('ok'):
                update_sync_status(user_id, 'github', 'failed')
                return {"success": False, "error": result.get('error')}
            
            repos = result.get('repos', [])
            
            # Process repo data
            processed_data = {
                'total_repos': len(repos),
                'languages': list(set([r.get('language') for r in repos if r.get('language')])),
                'total_stars': sum([r.get('stars', 0) for r in repos]),
                'repos': repos[:50],  # Limit to 50 most recent
                'last_synced': str(asyncio.get_event_loop().time())
            }
            
            # Cache for 30 minutes
            CacheManager.set(cache_key, processed_data, ttl_seconds=1800, user_id=user_id)
            update_sync_status(user_id, 'github', 'success')
            
            return {"success": True, "data": processed_data, "source": "api"}
            
        except Exception as e:
            update_sync_status(user_id, 'github', 'failed')
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def analyze_weaknesses(user_id: int, leetcode_data: Dict) -> List[Dict]:
        """
        AI-powered weakness analysis based on user data
        Uses caching and intelligent pattern detection
        """
        cache_key = f"weakness_analysis_{user_id}"
        cached = CacheManager.get(cache_key, user_id)
        if cached:
            return cached
        
        weaknesses = []
        
        # Analyze problem-solving patterns
        stats = leetcode_data.get('data', {})
        easy = stats.get('easy_solved', 0)
        medium = stats.get('medium_solved', 0)
        hard = stats.get('hard_solved', 0)
        
        # Weakness detection logic
        if medium < 20:
            weaknesses.append({
                'weakness_type': 'topic',
                'weakness_name': 'Medium Difficulty Problems',
                'severity_score': 8.0,
                'confidence': 0.9,
                'evidence': {'medium_solved': medium, 'threshold': 20},
                'recommendations': [
                    'Focus on medium-level dynamic programming',
                    'Practice graph algorithms',
                    'Study greedy algorithms'
                ],
                'ai_analysis': f'You have solved only {medium} medium problems. Aim for at least 50 to build strong fundamentals.'
            })
        
        if hard < 5:
            weaknesses.append({
                'weakness_type': 'topic',
                'weakness_name': 'Hard Problems',
                'severity_score': 9.0,
                'confidence': 0.85,
                'evidence': {'hard_solved': hard, 'threshold': 5},
                'recommendations': [
                    'Start with easier hard problems',
                    'Focus on advanced DP and graphs',
                    'Practice system design problems'
                ],
                'ai_analysis': f'Only {hard} hard problems solved. These are crucial for top-tier interviews.'
            })
        
        # Analyze recent submissions for patterns
        recent = stats.get('recent_submissions', [])
        if len(recent) < 5:
            weaknesses.append({
                'weakness_type': 'pattern',
                'weakness_name': 'Consistency',
                'severity_score': 7.0,
                'confidence': 0.8,
                'evidence': {'recent_count': len(recent)},
                'recommendations': ['Practice daily', 'Set a goal of 1-2 problems per day'],
                'ai_analysis': 'Low recent activity detected. Consistency is key for interview preparation.'
            })
        
        # Save to database
        for weakness in weaknesses:
            save_weakness_analysis(user_id, weakness)
        
        # Cache for 1 hour
        CacheManager.set(cache_key, weaknesses, ttl_seconds=3600, user_id=user_id)
        
        return weaknesses
    
    @staticmethod
    async def full_sync(user_id: int, force_refresh: bool = False) -> Dict:
        """
        Perform full sync of all platforms
        Runs in parallel for optimal performance
        """
        # Run syncs in parallel
        leetcode_task = SyncService.sync_leetcode_data(user_id, force_refresh)
        github_task = SyncService.sync_github_data(user_id, force_refresh)
        
        leetcode_result, github_result = await asyncio.gather(
            leetcode_task, github_task, return_exceptions=True
        )
        
        # Analyze weaknesses if LeetCode sync succeeded
        weaknesses = []
        if isinstance(leetcode_result, dict) and leetcode_result.get('success'):
            weaknesses = await SyncService.analyze_weaknesses(user_id, leetcode_result)
        
        return {
            'leetcode': leetcode_result,
            'github': github_result,
            'weaknesses': weaknesses,
            'timestamp': str(asyncio.get_event_loop().time())
        }
