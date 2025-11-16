# integration/main_pipeline.py
"""
Main integration pipeline that orchestrates:
1. User data analysis from Excel/PDFs
2. Problem tracking from multiple sources
3. Weakness profile generation
4. Personalized roadmap creation
5. Slack/Discord notifications
"""

import os
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

# Import modules
from analyzer.user_data_analyzer import UserDataAnalyzer
from tracker.enhanced_tracker import ProblemTracker, schedule_daily_summary
from roadmap.enhanced_generator import EnhancedRoadmapGenerator
from memory.db import get_weaknesses, insert_snapshot


class MAAnGMentorPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, data_dir: str = "./userData"):
        self.data_dir = Path(data_dir)
        self.analyzer = UserDataAnalyzer(data_dir)
        self.tracker = ProblemTracker()
        self.generator = EnhancedRoadmapGenerator()
        self.execution_log = []
        
    def run_full_pipeline(self, enable_notifications: bool = True) -> Dict:
        """Run the complete analysis pipeline."""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "steps": {},
            "summary": {}
        }
        
        # Step 1: Analyze user data
        print("\n" + "="*60)
        print("STEP 1: Analyzing User Data Files")
        print("="*60)
        
        user_data_results = self._analyze_user_data()
        results["steps"]["user_data_analysis"] = user_data_results
        
        # Step 2: Fetch and classify problems from external sources
        print("\n" + "="*60)
        print("STEP 2: Fetching Problems from External Sources")
        print("="*60)
        
        external_problems = self._fetch_external_problems()
        results["steps"]["external_sources"] = external_problems
        
        # Step 3: Update weakness profile
        print("\n" + "="*60)
        print("STEP 3: Updating Weakness Profile")
        print("="*60)
        
        weakness_results = self._update_weakness_profile(
            user_data_results["problems"] + external_problems.get("leetcode", [])
        )
        results["steps"]["weakness_profile"] = weakness_results
        
        # Step 4: Generate personalized roadmap
        print("\n" + "="*60)
        print("STEP 4: Generating Personalized Roadmap")
        print("="*60)
        
        roadmap = self._generate_roadmap()
        results["steps"]["roadmap"] = roadmap
        
        # Step 5: Send notifications
        if enable_notifications:
            print("\n" + "="*60)
            print("STEP 5: Sending Notifications")
            print("="*60)
            
            notification_results = self._send_notifications()
            results["steps"]["notifications"] = notification_results
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        # Export results
        self._export_results(results)
        
        return results
    
    def _analyze_user_data(self) -> Dict:
        """Step 1: Analyze user data files."""
        print("\n📊 Parsing Excel tracker...")
        problems = self.analyzer.analyze_excel_tracker()
        
        print("📚 Extracting PDF topics...")
        pdf_topics = self.analyzer.extract_pdf_topics()
        
        print("💪 Generating weakness profile from user data...")
        weakness_profile = self.analyzer.generate_weakness_profile()
        
        print("🎯 Creating personalized study plan...")
        recommendations = self.analyzer.recommend_study_plan(weakness_profile)
        
        results = {
            "problems_parsed": len(problems),
            "weakness_profile": weakness_profile,
            "pdf_topics_extracted": len([t for topics in pdf_topics.values() for t in topics]),
            "recommendations_generated": len(recommendations),
            "top_weaknesses": recommendations[:3]
        }
        
        # Log execution
        self.execution_log.append({
            "step": "user_data_analysis",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ User data analysis complete: {len(problems)} problems, {len(recommendations)} recommendations")
        return results
    
    def _fetch_external_problems(self) -> Dict:
        """Step 2: Fetch problems from external sources."""
        results = {
            "leetcode": [],
            "geeksforgeeks": [],
            "takeuforward": []
        }
        
        # Fetch LeetCode
        if self.tracker.leetcode_username:
            print(f"📌 Fetching LeetCode problems for {self.tracker.leetcode_username}...")
            lc_problems = self.tracker.process_leetcode_problems(self.tracker.leetcode_username)
            results["leetcode"] = lc_problems
            print(f"✅ Fetched {len(lc_problems)} LeetCode submissions")
        
        # Fetch GeeksforGeeks
        if self.tracker.gfg_username:
            print(f"📌 Fetching GeeksforGeeks problems...")
            gfg_problems = self.tracker.process_geeksforgeeks_problems(self.tracker.gfg_username)
            results["geeksforgeeks"] = gfg_problems
            print(f"✅ Fetched {len(gfg_problems)} GeeksforGeeks topics")
        
        # Fetch TakeUForward
        print("📌 Fetching TakeUForward curriculum...")
        tuf_modules = self.tracker.process_takeuforward_problems()
        results["takeuforward"] = tuf_modules
        print(f"✅ Fetched {len(tuf_modules)} TakeUForward modules")
        
        # Log execution
        self.execution_log.append({
            "step": "external_sources",
            "status": "completed",
            "leetcode_count": len(results["leetcode"]),
            "gfg_count": len(results["geeksforgeeks"]),
            "tuf_count": len(results["takeuforward"]),
            "timestamp": datetime.now().isoformat()
        })
        
        return results
    
    def _update_weakness_profile(self, all_problems: list) -> Dict:
        """Step 3: Update weakness profile in database."""
        print("🔄 Updating weakness profile...")
        
        self.tracker.update_weakness_profile(all_problems)
        
        weaknesses = get_weaknesses(limit=15)
        
        results = {
            "total_topics": len(weaknesses),
            "top_weaknesses": weaknesses[:5],
            "avg_weakness_score": sum([w.get("score", 0) for w in weaknesses]) // len(weaknesses) if weaknesses else 0
        }
        
        print(f"✅ Weakness profile updated: {len(weaknesses)} topics tracked")
        return results
    
    def _generate_roadmap(self) -> List[Dict]:
        """Step 4: Generate personalized roadmap."""
        print("🗺️ Generating personalized roadmap...")
        
        roadmap = self.generator.generate(limit=10)
        
        # Export roadmap in markdown
        md_roadmap = self.generator.export_roadmap(format="markdown")
        with open("ROADMAP_GENERATED.md", "w") as f:
            f.write(md_roadmap)
        
        print(f"✅ Roadmap generated: {len(roadmap)} topics with milestones")
        return roadmap
    
    def _send_notifications(self) -> Dict:
        """Step 5: Send Slack/Discord notifications."""
        results = {
            "slack_sent": False,
            "discord_sent": False,
            "errors": []
        }
        
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        
        if slack_webhook or discord_webhook:
            print("📤 Sending notifications...")
            
            try:
                self.tracker.send_daily_summary(slack_webhook, discord_webhook)
                if slack_webhook:
                    results["slack_sent"] = True
                if discord_webhook:
                    results["discord_sent"] = True
                print("✅ Notifications sent successfully")
            except Exception as e:
                results["errors"].append(str(e))
                print(f"⚠️ Notification error: {e}")
        else:
            print("⏭️ Skipping notifications (no webhooks configured)")
        
        # Schedule daily summaries if APScheduler available
        try:
            schedule_daily_summary(slack_webhook, discord_webhook)
            results["scheduler_active"] = True
        except Exception as e:
            results["scheduler_error"] = str(e)
        
        return results
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate execution summary."""
        return {
            "timestamp": results["timestamp"],
            "pipeline_status": "completed",
            "user_data_problems": results["steps"]["user_data_analysis"]["problems_parsed"],
            "external_sources_total": (
                len(results["steps"]["external_sources"].get("leetcode", [])) +
                len(results["steps"]["external_sources"].get("geeksforgeeks", [])) +
                len(results["steps"]["external_sources"].get("takeuforward", []))
            ),
            "weakness_topics_tracked": results["steps"]["weakness_profile"]["total_topics"],
            "roadmap_topics": len(results["steps"]["roadmap"]),
            "notifications_enabled": any([
                results["steps"].get("notifications", {}).get("slack_sent"),
                results["steps"].get("notifications", {}).get("discord_sent")
            ])
        }
    
    def _export_results(self, results: Dict):
        """Export results to JSON."""
        output_file = f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 Results exported to {output_file}")
        
        # Also export execution log
        log_file = "execution_log.json"
        with open(log_file, "w") as f:
            json.dump(self.execution_log, f, indent=2)
        
        print(f"📝 Execution log saved to {log_file}")


def main():
    """Main entry point."""
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║        MAANG MENTOR - FULL PIPELINE               ║
    ║   Intelligent Weakness Detection & Study Plans    ║
    ╚═══════════════════════════════════════════════════╝
    """)
    
    # Initialize pipeline
    pipeline = MAAnGMentorPipeline()
    
    # Run full pipeline
    results = pipeline.run_full_pipeline(enable_notifications=True)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    summary = results["summary"]
    print(f"✅ Pipeline Status: {summary['pipeline_status']}")
    print(f"📊 User Data Problems: {summary['user_data_problems']}")
    print(f"🌐 External Source Problems: {summary['external_sources_total']}")
    print(f"💪 Topics Tracked: {summary['weakness_topics_tracked']}")
    print(f"🗺️ Roadmap Topics: {summary['roadmap_topics']}")
    print(f"📤 Notifications: {'Enabled' if summary['notifications_enabled'] else 'Disabled'}")
    
    print("\n" + "="*60)
    print("📚 Generated Files:")
    print("="*60)
    print("  • ROADMAP_GENERATED.md - Detailed study roadmap")
    print(f"  • pipeline_results_*.json - Full analysis results")
    print("  • execution_log.json - Execution timeline")
    print("  • analysis_report.json - User data analysis")


if __name__ == "__main__":
    main()
