#!/usr/bin/env python3
"""
Database Management Script for AI Content Creator
Use this to view, manage, and analyze your database data
"""

from db import get_client, get_recent_content
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def show_database_stats():
    """Display comprehensive database statistics"""
    try:
        # Get database client
        client = get_client()
        
        # Get recent content
        content = get_recent_content(limit=10)
        
        # Query specific tables
        users = client.table('users').select('*').execute()
        sources = client.table('sources').select('*').execute()
        newsletters = client.table('newsletters').select('*').execute()
        
        print("=" * 50)
        print("📊 DATABASE STATISTICS")
        print("=" * 50)
        
        # Users
        print(f"👥 Users: {len(users.data)}")
        for user in users.data:
            print(f"   - {user['email']} ({user['name']}) - Created: {user['created_at']}")
        
        # Sources
        print(f"\n📰 Sources: {len(sources.data)}")
        categories = {}
        for source in sources.data:
            cat = source['category']
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        for cat, count in categories.items():
            print(f"   - {cat}: {count} sources")
        
        # Content
        print(f"\n📄 Content Items: {len(content)}")
        if content:
            print("   Recent content:")
            for item in content[:3]:
                print(f"   - {item.get('title', 'Untitled')[:50]}...")
                print(f"     Source: {item.get('source_url', 'N/A')}")
                print(f"     Created: {item.get('created_at', 'N/A')}")
        
        # Newsletters
        print(f"\n📧 Newsletters: {len(newsletters.data)}")
        for newsletter in newsletters.data:
            status = newsletter['status']
            title = newsletter['title']
            scheduled = newsletter['scheduled_at']
            print(f"   - {title} ({status}) - Scheduled: {scheduled}")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def search_content(keyword):
    """Search content by keyword"""
    try:
        client = get_client()
        
        # Search in content table
        result = client.table('content').select('*').ilike('title', f'%{keyword}%').execute()
        
        print(f"🔍 Search results for '{keyword}': {len(result.data)} items found")
        
        for item in result.data:
            print(f"\n📰 {item['title']}")
            print(f"   Source: {item['source_url']}")
            print(f"   Summary: {item['summary'][:100]}...")
            print(f"   Created: {item['created_at']}")
            
    except Exception as e:
        print(f"❌ Search error: {e}")

def list_sources_by_category(category=None):
    """List all sources, optionally filtered by category"""
    try:
        client = get_client()
        
        if category:
            result = client.table('sources').select('*').eq('category', category).execute()
            print(f"📰 Sources in '{category}' category:")
        else:
            result = client.table('sources').select('*').execute()
            print("📰 All Sources:")
        
        for source in result.data:
            status = "✅ Active" if source['is_active'] else "❌ Inactive"
            print(f"   - {source['name']} ({source['type']}) - {status}")
            print(f"     URL: {source['url']}")
            print(f"     Description: {source['description']}")
            print()
            
    except Exception as e:
        print(f"❌ Error listing sources: {e}")

def main():
    """Main function with interactive menu"""
    while True:
        print("\n" + "=" * 50)
        print("🗄️  DATABASE MANAGER")
        print("=" * 50)
        print("1. Show database statistics")
        print("2. Search content by keyword")
        print("3. List sources by category")
        print("4. List all sources")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            show_database_stats()
        elif choice == '2':
            keyword = input("Enter keyword to search: ").strip()
            if keyword:
                search_content(keyword)
        elif choice == '3':
            category = input("Enter category (AI, Machine Learning, Tech News, Data Science, General News): ").strip()
            if category:
                list_sources_by_category(category)
        elif choice == '4':
            list_sources_by_category()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
