from database import init_db, get_db
from travel_logic import create_trip, add_activity, vote_for_item, finalize_proposal, get_schedule_items
from datetime import date, time

def run_test():
    print("🚀 開始功能驗證測試...")
    
    # 1. Initialize DB
    init_db()
    db = get_db()
    
    # 2. Create a Trip
    print("--- 建立行程 ---")
    trip = create_trip(db, "測試旅遊", date(2026, 7, 1), date(2026, 7, 3))
    print(f"行程建立成功：{trip.title}, 邀請碼：{trip.invite_code}")
    
    # 3. Add a fixed activity
    print("--- 新增固定行程 ---")
    add_activity(db, trip.id, 1, "抵達機場", time(10, 0), 60, "成田機場", "記得取行李")
    items = get_schedule_items(db, trip.id, 1)
    print(f"Day 1 行程數：{len(items)}, 第一項：{items[0].title}")
    
    # 4. Add a proposal and vote
    print("--- 測試投票機制 ---")
    prop = add_activity(db, trip.id, 1, "燒肉午餐 (提案)", is_proposal=True)
    vote_for_item(db, prop.id, "Alice")
    vote_for_item(db, prop.id, "Bob")
    
    # Reload items to see votes
    items = get_schedule_items(db, trip.id, 1)
    prop_item = next(i for i in items if i.is_proposal)
    print(f"提案「{prop_item.title}」票數：{len(prop_item.votes)}")
    
    # 5. Finalize proposal
    print("--- 測試定案 ---")
    finalize_proposal(db, prop_item.id)
    items = get_schedule_items(db, trip.id, 1)
    fixed_item = next(i for i in items if i.title == "燒肉午餐 (提案)")
    print(f"定案狀態 (is_proposal): {fixed_item.is_proposal}")
    
    print("\n✅ 所有功能驗證完成！")

if __name__ == "__main__":
    run_test()
