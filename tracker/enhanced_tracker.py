# tracker/enhanced_tracker.py
"""
Enhanced problem tracker with topic classification and notification support.
Classifies problems by topic tags from LeetCode, GeeksforGeeks, and TakeUForward.
Supports Slack/Discord webhooks for daily summaries.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from memory.db import upsert_weakness, get_weaknesses, insert_snapshot, get_latest_snapshot

# Topic classification mapping
TOPIC_DIFFICULTY_MAP = {
    "array": 2,
    "string": 2,
    "hash-table": 2,
    "linked-list": 3,
    "stack": 2,
    "queue": 2,
    "tree": 4,
    "binary-search-tree": 4,
    "graph": 5,
    "backtracking": 4,
    "dynamic-programming": 5,
    "greedy": 3,
    "sorting": 2,
    "bit-manipulation": 3,
    "math": 3,
    "geometry": 4,
    "database": 3,
    "design": 4,
    "system-design": 5,
}

class ProblemTracker:
    """Track problems solved and classify by topic."""
    
    def __init__(self):
        self.github_username = os.getenv("GITHUB_USERNAME", "")
        self.leetcode_username = os.getenv("LEETCODE_USERNAME", "")
        self.gfg_username = os.getenv("GFG_USERNAME", "")
        self.tuf_username = os.getenv("TUF_USERNAME", "")
        
    def classify_problem(self, title: str, tags: List[str], difficulty: str) -> Dict:
        """Classify a problem and extract topic information."""
        # Normalize topic tags
        topics = [tag.lower().strip() for tag in tags]
        primary_topic = topics[0] if topics else "general"
        
        # Calculate difficulty score (1-5)
        difficulty_score = {
            "easy": 1,
            "medium": 3,
            "hard": 5
        }.get(difficulty.lower(), 2)
        
        # Get base topic difficulty
        base_difficulty = TOPIC_DIFFICULTY_MAP.get(primary_topic, 3)
        
        return {
            "title": title,
            "topics": topics,
            "primary_topic": primary_topic,
            "difficulty": difficulty,
            "difficulty_score": difficulty_score,
            "combined_score": (difficulty_score + base_difficulty) // 2,
            "classified_at": datetime.now().isoformat()
        }
    
    def process_leetcode_problems(self, username: str) -> List[Dict]:
        """Fetch and classify LeetCode problems."""
        problems = []
        try:
            # LeetCode GraphQL endpoint
            query = """
            query getProblems($username: String!) {
              allQuestionsCount {
                totalQuestions
              }
              matchedUser(username: $username) {
                submitStats {
                  acSubmissionNum {
                    count
                    difficulty
                  }
                }
              }
            }
            """
            
            response = requests.post(
                "https://leetcode.com/graphql",
                json={"query": query, "variables": {"username": username}},
                headers={"User-Agent": "maang-agent"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {}).get("matchedUser", {}).get("submitStats", {})
                submissions = stats.get("acSubmissionNum", [])
                
                for submission in submissions:
                    difficulty = submission.get("difficulty", "Medium")
                    count = submission.get("count", 0)
                    if count > 0:
                        problems.append({
                            "source": "leetcode",
                            "difficulty": difficulty,
                            "count": count,
                            "topic": f"LeetCode {difficulty}",
                            "tags": [difficulty.lower()]
                        })
            
            # Store snapshot
            insert_snapshot("leetcode", username, {
                "problems": problems,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error fetching LeetCode problems: {e}")
        
        return problems
    
    def process_geeksforgeeks_problems(self, username: str) -> List[Dict]:
        """Scrape GeeksforGeeks explore page for problem tags."""
        problems = []
        try:
            # Fetch GeeksforGeeks explore page
            url = "https://www.geeksforgeeks.org/explore?page=1&sortBy=submissions"
            response = requests.get(url, headers={"User-Agent": "maang-agent"}, timeout=10)
            
            if response.status_code == 200:
                # Parse problem tags from the explore page
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract problem cards (adjust selectors based on actual HTML)
                problem_tags = set()
                for tag in soup.find_all("span", class_="topic-tag"):
                    if tag.text:
                        problem_tags.add(tag.text.strip().lower())
                
                for tag in sorted(problem_tags):
                    problems.append({
                        "source": "geeksforgeeks",
                        "topic": tag,
                        "tags": [tag],
                        "url": f"https://www.geeksforgeeks.org/explore?topic={tag}"
                    })
            
            # Store snapshot
            insert_snapshot("geeksforgeeks", username or "explore", {
                "problems": problems,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error fetching GeeksforGeeks problems: {e}")
        
        return problems
    
    def process_takeuforward_problems(self) -> List[Dict]:
        """Parse TakeUForward DSA curriculum."""
        problems = []
        try:
            url = "https://takeuforward.org/plus/dsa/"
            response = requests.get(url, headers={"User-Agent": "maang-agent"}, timeout=10)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract modules/topics from TakeUForward curriculum
                modules = soup.find_all("div", class_="module")
                for module in modules:
                    title = module.find("h3", class_="module-title")
                    if title:
                        topic = title.text.strip().lower()
                        problems.append({
                            "source": "takeuforward",
                            "topic": topic,
                            "tags": [topic],
                            "url": f"https://takeuforward.org/plus/dsa/"
                        })
            
            # Store snapshot
            insert_snapshot("takeuforward", "curriculum", {
                "modules": problems,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error fetching TakeUForward curriculum: {e}")
        
        return problems
    
    def update_weakness_profile(self, problems: List[Dict]):
        """Update weakness profile based on classified problems."""
        weakness_counts = {}
        
        for problem in problems:
            topic = problem.get("primary_topic") or problem.get("topic", "general")
            score = problem.get("combined_score", 2)
            
            if topic not in weakness_counts:
                weakness_counts[topic] = {"count": 0, "total_score": 0}
            
            weakness_counts[topic]["count"] += 1
            weakness_counts[topic]["total_score"] += score
        
        # Upsert weaknesses (higher score = more struggled)
        for topic, data in weakness_counts.items():
            avg_score = data["total_score"] // data["count"]
            # Reverse: we want to track gaps (low success rate as weakness)
            weakness_score = 100 - (avg_score * 20)  # Scale to 0-100
            upsert_weakness(topic, max(1, weakness_score))
    
    def send_daily_summary(self, slack_webhook: Optional[str] = None, 
                          discord_webhook: Optional[str] = None):
        """Send daily summary to Slack/Discord."""
        weaknesses = get_weaknesses(limit=10)
        
        if not weaknesses:
            return
        
        summary = self._format_summary(weaknesses)
        
        if slack_webhook:
            self._send_slack_notification(slack_webhook, summary, weaknesses)
        
        if discord_webhook:
            self._send_discord_notification(discord_webhook, summary, weaknesses)
    
    def _format_summary(self, weaknesses: List[Dict]) -> str:
        """Format weakness summary for notifications."""
        lines = [
            "🎯 **MAANG Mentor - Daily Weakness Report**",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📊 Top Weak Topics:",
        ]
        
        for i, w in enumerate(weaknesses[:5], 1):
            topic = w.get("topic", "Unknown")
            score = w.get("score", 0)
            lines.append(f"  {i}. **{topic}** (Score: {score})")
        
        return "\n".join(lines)
    
    def _send_slack_notification(self, webhook_url: str, summary: str, weaknesses: List[Dict]):
        """Send notification to Slack."""
        try:
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🎯 MAANG Mentor Daily Report",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": summary
                        }
                    },
                    {
                        "type": "divider"
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Dashboard",
                                    "emoji": True
                                },
                                "value": "dashboard",
                                "url": "http://localhost:5100"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✅ Slack notification sent at {datetime.now()}")
        except Exception as e:
            print(f"❌ Slack notification failed: {e}")
    
    def _send_discord_notification(self, webhook_url: str, summary: str, weaknesses: List[Dict]):
        """Send notification to Discord."""
        try:
            embed = {
                "title": "🎯 MAANG Mentor Daily Report",
                "description": summary.replace("**", "**"),
                "color": 16711680,  # Red color
                "fields": [
                    {
                        "name": "📊 Top Weak Topics",
                        "value": "\n".join([
                            f"**{w.get('topic')}** (Score: {w.get('score')})"
                            for w in weaknesses[:5]
                        ]),
                        "inline": False
                    }
                ],
                "footer": {
                    "text": f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
            
            payload = {"embeds": [embed]}
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✅ Discord notification sent at {datetime.now()}")
        except Exception as e:
            print(f"❌ Discord notification failed: {e}")


# Scheduler for daily summaries
def schedule_daily_summary(slack_webhook: Optional[str] = None, 
                          discord_webhook: Optional[str] = None):
    """Schedule daily summary notifications at a specific time (e.g., 9 AM)."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        tracker = ProblemTracker()
        
        scheduler = BackgroundScheduler()
        
        # Schedule for 9 AM daily
        scheduler.add_job(
            tracker.send_daily_summary,
            CronTrigger(hour=9, minute=0),
            args=[slack_webhook, discord_webhook],
            id="daily_summary",
            replace_existing=True
        )
        
        scheduler.start()
        print("✅ Daily summary scheduler started (9 AM daily)")
        return scheduler
    except ImportError:
        print("⚠️ APScheduler not installed. Install with: pip install apscheduler")
        return None
