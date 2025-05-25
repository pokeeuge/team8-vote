import streamlit as st
import pandas as pd
import altair as alt
import streamlit.components.v1 as components
import gspread
from google.oauth2.service_account import Credentials

# ===========================
# 🔐 Google Sheets 認證
# ===========================

# 從 .streamlit/secrets.toml 讀取憑證
try:
    service_account_info = st.secrets["gcp"]
except Exception as e:
    st.error(f"無法讀取 secrets：{e}")
    st.stop()

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# 建立憑證
credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

# gspread 授權
gc = gspread.authorize(credentials)

# 開啟 Google Sheets
try:
    SHEET = gc.open("Team8_Votes").worksheet("Sheet1")  # 確保建立好 Sheet 並分享給服務帳號
except Exception as e:
    st.error(f"無法開啟 Google Sheet：{e}")
    st.stop()

# === 限定名單 (Whitelist) ===
allowed_voters = [
    "Annie Yao", "Ashley Shih", "Carmelo Lin", "Chris Wu", "Danny Lim",
    "Fanny Ting", "JC Khoo", "Jill Yu", "Joanne Chen", "Lily Wang", "Max Chen", "Susan Lee"
]

# --- Page Title ---
st.set_page_config(page_title="Team 8 Lunch Meetup")
st.title("🏃‍♀️ Team 8 Lunch Meetup")

name = st.text_input("📝 Enter your name｜請輸入你的名字：").strip()

# 讀取 Google Sheets 最新資料
votedata = SHEET.get_all_records()
# st.write("Google Sheets 內容：", data)


# 轉成 DataFrame
if votedata:  # 有資料（標頭 + 至少一筆資料）
    df = pd.DataFrame(votedata)
    # 標準化欄位名稱
    df.columns = [col.strip().lower() for col in df.columns]
    # 標準化每一行資料的值：去空白、轉小寫
    df = df.applymap(lambda x: x.strip().lower() if isinstance(x, str) else x)
else:  # 只有標頭（沒資料）
    df = pd.DataFrame(columns=['name', 'type', 'vote'])

# 顯示欄位結構
# st.write("資料欄位:", df.columns.tolist())
route_df = df[df['type'] == 'route']
# st.write("✅ route_df:", route_df)
# st.write("資料內容:", df)

if name:
    if name not in allowed_voters:
        st.error("❌ 你不在投票名單內，請聯繫管理員")
        st.stop()
    else:
        st.success(f"Hi {name}！請繼續投票！")

# --- 🙏 Purpose & Gratitude ---
st.header("🙏 Purpose & Gratitude｜目的與感謝")
st.write("""
This lunch meetup is to thank everyone for your efforts during the step challenge — whether you walked a lot or a little, you're part of what makes Team 8 great!
Let's take this chance to regroup, review our progress, vote on our team name, and enjoy pizza together!
""")
st.write("""
😊 這次聚會是對大家這段時間努力的感謝，也是我們團隊補充能量的時刻。
""")

# ✨ Step Challenge Analysis｜步數挑戰分析
st.markdown("""
## ✨ Step Challenge Analysis｜步數挑戰分析

📊 目前總步數為 **1,077,201 步**  
🥇 超越第一名需達到 **2,104,176 步**  
📉 等於還差 **1,026,975 步**

🏔️ **象山加分最高為 55,000 步**（少於5人無效）

🚶‍♀️🚶‍♂️ 如果沒有人參加，全隊平均每人將需額外走 **85,581 步**  
🎯 參加人越多，其他人平均步數負擔越小

---

** Explanation (For clarity)**

We’re currently about **950,000 steps** behind the top team.  
To catch up, we need to collectively add extra steps.

There’s a **bonus system** for hiking Xiangshan:

- **Maximum bonus is 55,000 steps** (total for the whole team)
- **Only valid if at least 5 teammates participate**
- **Bonus is scaled by number of participants**  
  e.g., 6 people → 55,000 × 6 ÷ 12 = 27,500 steps

---

🔍 **What this table shows:**

| Column | Meaning |
|--------|---------|
| **Participants** | Number of teammates going to Xiangshan |
| **Effective Bonus** | Steps added to team total if eligible |
| **Remaining Steps** | Steps still needed after bonus to pass 1st place |
| **Per Person Required** | Extra steps each teammate would need to contribute if split evenly |
| **Feasible** | Whether that step count is within the 200,000 max per person limit |

""")

# === Xiangshan Bonus Table 說明 ===
st.header("📈 Xiangshan Bonus Table｜象山加分表說明")
team_size = len(allowed_voters)
xiangshan_bonus = 55000
total_steps = 1146027
target_avg = 175348
target_total = target_avg * team_size
remaining_steps = target_total - total_steps

bonus_data = []
for x in range(0, team_size + 1):
    bonus = 0 if x < 5 else xiangshan_bonus * x / team_size
    remaining = remaining_steps - bonus
    per_person = remaining / team_size
    feasible = per_person <= 200000
    bonus_data.append({
          "Participants｜參加人數": x,
          "Effective Bonus｜有效加分": round(bonus),
          "Remaining Steps｜剩餘步數": round(remaining),
          "Per Person｜每人需補": round(per_person),
          "Feasible｜可行？": feasible
            })
    bonus_df = pd.DataFrame(bonus_data)
st.dataframe(bonus_df)

# --- 📊 Step Challenge Progress ---
st.header("📊 進度分配｜Step Challenge Progress")
data = {
    "Name": ["Annie Yao", "Ashley Shih", "Carmelo Lin", "Chris Wu", "Danny Lim", "Fanny Ting", "JC Khoo", "Jill Yu", "Joanne Chen", "Lily Wang", "Max Chen", "Susan Lee"],
    "Steps_Recorded": [85895, 103755, 94809, 96134, 100107, 93328, 105953, 92161, 84912, 69979, 211115, 59983]
}
df = pd.DataFrame(data)
df["Capped_Steps"] = df["Steps_Recorded"].apply(lambda x: min(x, 100000))
total_steps = df["Capped_Steps"].sum()
team_size = len(df)
target_avg = 175348
target_total = target_avg * team_size
remaining_steps = target_total - total_steps
df["Target_Share"] = df["Capped_Steps"] / total_steps * remaining_steps
st.dataframe(df[["Name", "Capped_Steps", "Target_Share"]])

st.header("💡 Summary (總結)")
summary_table = """
- **85,000怎麼來？ / How 85,000 comes from?**  
  估計目前與目標差距約 958,149，大約 **79,845/人**  
  Estimated gap: ~958,149 steps, ~79,845 per person

- **跟哪一隊比？ / Compared to which team?**  
  第一名平均 **175,348**  
  The 1st team's average is **175,348**

- **是否所有人要補這些？ / Everyone needs to cover?**  
  是，如果沒有人參加象山，全隊需要分擔的步數就多  
  Yes, if no one joins Elephant Mountain, others need to share more steps

- **第三名會追上嗎？ / Will the 3rd team catch up?**  
  除非我們停止，不然第三隊要追過這兩週需要每個人平均 **83,233**  
  Unless we stop, they need ~83,233 per person in 2 weeks
"""
st.markdown(summary_table)
st.markdown("""
The more people we get to hike Xiangshan, the less each of us needs to walk extra.  
But we need at least **5 participants** for the bonus to count.

This chart helps us decide how many people we should aim to mobilize.
""")

# --- 🗺️ Elephant Mountain Route Plan ---
st.header("🗺️ Elephant Mountain Route Options｜象山路線規劃")
st.markdown("""
**Route Options 路線選擇：**

- **Trailhead Route 登山口路線**  
  ↳ 290 meters, +77m elevation (stairs)｜290 公尺，上升 77 公尺（樓梯）

- **Songde Route 松德路線**  
  ↳ 290 meters, +43m elevation (stairs, gentle slope)｜290 公尺，上升 43 公尺（樓梯+緩坡）

- **Lingyin Trail 靈隱寺象山步道**  
  ↳ 950 meters, +13m up / -43m down (starts uphill, then flat and descent)｜950 公尺，上升 13 公尺，下降 43 公尺 （起初爬升，接著平緩再下坡）        

**Interactive Map: Trailhead to Shooting Platform｜互動地圖：從登山口到攝手平台**
""")

# --- 🗺️ Embedded Google Map with Route ---
components.iframe(
    "https://www.google.com/maps/embed?pb=!1m28!1m12!1m3!1d1520.0004481506185!2d121.571501535416!3d25.02760173531343!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!4m13!3e2!4m5!1s0x3442ab1950005a23%3A0x907b0e39bfb279f6!2zMTEw5Y-w5YyX5biC5L-h576p5Y2A6LGh5bGx5q2l6YGT!3m2!1d25.027375!2d121.5709619!4m5!1s0x3442abac555affb3%3A0xffe76f0c848eef86!2z5Y-w5YyX5biC5L-h576p5Y2A5pSd5omL5bmz5Y-w!3m2!1d25.027191499999997!2d121.5731835!5e0!3m2!1szh-TW!2stw!4v1748046831357!5m2!1szh-TW!2stw",
    height=450
)

st.markdown("""
**Alternate Route: 三犁里到象山攝手平台**
""")
components.iframe(
    "https://www.google.com/maps/embed?pb=!1m26!1m12!1m3!1d1556.9230116431659!2d121.57432318814976!3d25.02779699889496!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!4m11!3e2!4m3!3m2!1d25.028212999999997!2d121.5752978!4m5!1s0x3442abac555affb3%3A0xffe76f0c848eef86!2z5Y-w5YyX5biC5L-h576p5Y2A5pSd5omL5bmz5Y-w!3m2!1d25.027191499999997!2d121.5731835!5e0!3m2!1szh-TW!2stw!4v1748072054311!5m2!1szh-TW!2stw",
    height=450
)
st.markdown("""
**Alternate Route 2: 靈隱寺通象山步道到攝手平台**
""")
components.iframe(
    "https://www.google.com/maps/embed?pb=!1m28!1m12!1m3!1d3113.9082390844155!2d121.57560186423432!3d25.025344980842437!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!4m13!3e2!4m5!1s0x3442abaa5aeb16fb%3A0x35328181a21c80b0!2zMTEw5Y-w5YyX5biC5L-h576p5Y2A6Z2I6Zqx5a-66YCa6LGh5bGx5q2l6YGT!3m2!1d25.0254044!2d121.580799!4m5!1s0x3442abac555affb3%3A0xffe76f0c848eef86!2z5Y-w5YyX5biC5L-h576p5Y2A5pSd5omL5bmz5Y-w!3m2!1d25.027191499999997!2d121.5731835!5e0!3m2!1szh-TW!2stw!4v1748072167777!5m2!1szh-TW!2stw",
    height=450
)

st.markdown("""
---
### 📝 象山健行注意事項與準備清單｜Elephant Mountain Hike Reminders & Checklist

- 🕐 **出發時間**｜Departure Time：中午出發，留意防曬與補水 Midday departure; bring sun protection and water
- 🌞 **防曬用品**｜Sun Protection：帽子、涼感噴霧必備 Hat & cooling spray essential
- 🦟 **防蚊提醒**｜Mosquito Protection：請攜帶防蚊液 Bring mosquito spray
- 🩹 **小傷處理**｜Injury Care：攜帶 OK 繃，留意階梯與石階 Bring band-aids; watch your step
- 💧 **補水需求**｜Hydration：每人至少 1 公升水 At least 1L of water per person

#### 🎒 建議攜帶物品｜Recommended Items
- 水｜Water (1L+)
- 帽子｜Hat
- 涼感噴霧｜Cooling spray
- 防蚊液｜Mosquito spray
- 毛巾｜Towel
- 能量補給｜Snacks (nuts, energy bar)
- OK 繃｜Band-aid
- 行動電源｜Powerbank
- 好心情｜Good mood!
""")


# === 🗳️ Route Voting ===
st.header("🗳️ Route Voting｜路線票選")
# 將路線選項也標準化為小寫
route_options_raw = ['trailhead route 登山口路線', 'songde route 松德路線', 'lingyin trail 靈隱寺象山步道']
route_options = [opt.lower() for opt in route_options_raw]

# 顯示投票選項（保持原樣顯示，底層用標準化小寫比對）
route_vote_display = st.radio("Pick your preferred route｜選擇你喜歡的路線：", route_options_raw)

if st.button("✅ Submit Route Vote｜提交路線投票"):
    if not name.strip():
        st.warning("❗ 請先輸入你的名字再進行投票！")
    else:
        # 存入 Google Sheets 時，vote 以小寫存儲，方便統計
        SHEET.append_row([name, "Route", route_vote_display.lower()])
        st.success(f"Your route vote「{route_vote_display}」 has been saved！")
        import time
        time.sleep(2)  # 等待 Google Sheets 更新
        st.rerun()

# === 顯示票數排名 ===
st.subheader("🏅 路線票數排名")
# st.write("DEBUG - Google Sheets 回傳的資料:", votedata)
if votedata:
    df = pd.DataFrame(votedata)
    # st.write("DEBUG - 轉成 DataFrame", df)
    df.columns = [col.strip().lower() for col in df.columns]
    # st.write("DEBUG - 欄位名稱", df.columns.tolist())
    df = df.applymap(lambda x: x.strip().lower() if isinstance(x, str) else x)
else:
    df = pd.DataFrame(columns=['name', 'type', 'vote'])
    
if not df.empty and 'type' in df.columns:
    route_df = df[df['type'] == 'route']
    if not route_df.empty:
        # 統計票數時，確保對齊小寫版本
        route_counts = route_df['vote'].value_counts().reindex(route_options, fill_value=0)
        st.bar_chart(route_counts)

        # # 顯示表格 (顯示原始格式)
        # display_counts = pd.DataFrame({
        #     '路線': route_options_raw,
        #     '票數': [route_counts.get(opt, 0) for opt in route_options]
        # })
        # st.dataframe(display_counts)
    else:
        st.info("目前沒有任何『Route』類型投票資料。")
else:
    st.info("尚無投票資料。")

# --- Team Name Descriptions ---
st.markdown("""
### 1. Shohei Blowtani  
**Blowout victory energy**  
- 靈感來自日本超人氣棒球選手 Shohei Ohtani（大谷翔平），結合英文單字 “blowout”，意思是「大勝、壓倒性勝利」。諧音梗，成了 “Blowtani”。  
- 象徵我們這組不只走路，還要一舉爆走、吹走對手！  
- 我們不比速度，我們是戰術制勝的 Blowtani！

---

### 2. 八八八八八 I'm lovin' it  
**Fun, rhythmic, culturally playful**  
- 取自麥當勞經典口號 “I’m lovin’ it”，搭配我們團隊專屬數字「八」。  
- 象徵我們就像是一群默默累積步數、卻默默上升的快閃王者！  
- I’m walkin’ it. Not just lovin’ it.

---

### 3. Blowtani 八八八八八  
**Hybrid with luck + power**  
- 這個是前兩個的融合精華版：結合「Shohei Blowtani」的強者氣勢與「八八八八八」的幸運步調。  
- 象徵我們這隊：有風格、有策略、有默契、有梗，爆走又旺起來！
""")

# --- Voting System with Voter Name ---
team_options_raw = ['Shohei Blowtani', '八八八 I\'m lovin\' it', 'Blowtani 八八八八八']
team_options = [opt.lower() for opt in team_options_raw]

team_vote_display = st.radio("Pick your favorite team name｜選出你最喜歡的隊名：", team_options_raw)

if st.button("✅ Submit Team Name Vote｜提交隊名投票"):
    if not name.strip():
        st.warning("❗ 請先輸入你的名字再進行投票！")
    else:
        SHEET.append_row([name, "TeamName", team_vote_display.lower()])
        st.success(f"Your team name vote「{team_vote_display}」has been saved!")
        import time
        time.sleep(2)  # 等待 Google Sheets 更新
        st.rerun()

st.subheader("🗳️ 隊名投票結果統計")
if not df.empty and 'type' in df.columns:
    team_df = df[df['type'] == 'teamname']
    # st.write("✅ team_df:", team_df)
    if not team_df.empty:
        team_counts = team_df['vote'].value_counts().reindex(team_options, fill_value=0)
        st.bar_chart(team_counts)

        # # 顯示表格 (原始隊名格式)
        # display_counts = pd.DataFrame({
        #     '隊名': team_options_raw,
        #     '票數': [team_counts.get(opt, 0) for opt in team_options]
        # })
        # st.dataframe(display_counts)
    else:
        st.info("目前沒有任何『TeamName』類型投票資料。")
else:
    st.info("尚無投票資料。")


# --- 🚀 Closing Words ---
st.header("🚀 Final Words")
st.markdown("""
Thanks again for being part of this amazing journey! 🚶‍♂️🚶‍♀️
Let's walk smart, walk proud — and Blow(tani) them away!
""")
