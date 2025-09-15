#!/usr/bin/env python3
"""
Quick script to check story status and scores
"""

from services.storage import TextStore

def main():
    storage = TextStore()
    stories = storage.get_all_stories()
    
    print(f"📊 Story Status Report")
    print(f"=" * 40)
    print(f"Total stories: {len(stories)}")
    
    # Count scored vs unscored
    scored = [s for s in stories if s.get('score', 0) > 0]
    unscored = [s for s in stories if s.get('score', 0) == 0]
    
    print(f"✅ Scored stories: {len(scored)}")
    print(f"⏳ Unscored stories: {len(unscored)}")
    
    if scored:
        scores = [s['score'] for s in scored]
        print(f"\n🎯 Score Distribution:")
        print(f"   Average: {sum(scores) / len(scores):.1f}")
        print(f"   Highest: {max(scores)}")
        print(f"   90-100:  {len([s for s in scores if s >= 90])}")
        print(f"   80-89:   {len([s for s in scores if 80 <= s < 90])}")
        print(f"   70-79:   {len([s for s in scores if 70 <= s < 80])}")
        print(f"   60-69:   {len([s for s in scores if 60 <= s < 70])}")
        
        print(f"\n🏆 Top 5 Stories:")
        top_stories = sorted(scored, key=lambda x: x.get('score', 0), reverse=True)[:5]
        for i, story in enumerate(top_stories, 1):
            print(f"   {i}. [{story['score']}] {story['title'][:60]}...")

if __name__ == "__main__":
    main()