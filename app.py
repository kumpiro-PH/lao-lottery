import streamlit as st
from datetime import datetime
from collections import Counter
from itertools import permutations
import re
import pandas as pd
import os

# =====================================================
# 1. PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="LAO AI PROFESSIONAL v4.1",
    page_icon="🧠",
    layout="centered"
)

VERSION = "4.1 HYBRID DAILY & PERMUTATION ENGINE (5-DAY CSV)"

# =====================================================
# 2. CSS - SKY BLUE MOBILE THEME
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}

.grid-container {
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(80px,1fr));
    gap:10px;
    margin-top:15px;
    margin-bottom:15px;
}

.stat-card {
    background:linear-gradient(135deg,#ffffff,#f0f9ff);
    border:1px solid #bae6fd;
    border-top:4px solid #0284c7;
    border-radius:12px;
    padding:12px 6px;
    text-align:center;
    box-shadow:0 2px 6px rgba(2,132,199,.08);
}

.stat-num {
    font-size:26px;
    font-weight:800;
    color:#0c4a6e;
}

.stat-count {
    font-size:12px;
    font-weight:600;
    color:#0369a1;
    background:#e0f2fe;
    padding:3px 8px;
    border-radius:12px;
    display:inline-block;
    margin-top:6px;
}

.pair-box {
    background:#f0f9ff;
    border-left:4px solid #0284c7;
    border-radius:8px;
    padding:12px;
    margin:12px 0;
}

.pair-title {
    font-weight:700;
    color:#0369a1;
    margin-bottom:8px;
}

.badge-number {
    display:inline-block;
    background:white;
    border:1px solid #7dd3fc;
    border-radius:6px;
    padding:5px 9px;
    margin:3px;
    font-weight:700;
    color:#0c4a6e;
    font-size:14px;
}

.badge-highlight {
    background:#0284c7;
    color:white;
    border-color:#0369a1;
}

.section-note {
    color:#64748b;
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# 3. DAILY NUMBERS & 5-DAY CSV MANAGEMENT
# =====================================================

DAILY_NUMBERS = {
    "Monday": "056787",
    "Tuesday": "657872",
    "Wednesday": "390768",
    "Thursday": "897693",
    "Friday": "305687"
}

DAY_NAMES_TH = {
    "Monday": "วันจันทร์",
    "Tuesday": "วันอังคาร",
    "Wednesday": "วันพุธ",
    "Thursday": "วันพฤหัสบดี",
    "Friday": "วันศุกร์"
}

# กำหนดชื่อไฟล์ CSV แยกตามวัน (เฉพาะ 5 วัน)
CSV_FILE_MAP = {
    "Monday": "history_lao_mon.csv",
    "Tuesday": "history_lao_tue.csv",
    "Wednesday": "history_lao_wed.csv",
    "Thursday": "history_lao_thu.csv",
    "Friday": "history_lao_fri.csv"
}

CURRENT_DAY = datetime.now().strftime("%A")
# หากเป็นวันเสาร์/อาทิตย์ ให้เลือกวันจันทร์เป็นค่าเริ่มต้น
DEFAULT_DAY = CURRENT_DAY if CURRENT_DAY in DAILY_NUMBERS else "Monday"

def get_daily_number(day):
    return DAILY_NUMBERS.get(day, "000000")

def load_day_history(day):
    filename = CSV_FILE_MAP.get(day)
    if filename and os.path.exists(filename):
        try:
            return pd.read_csv(filename, dtype=str)
        except Exception:
            pass
    return pd.DataFrame(columns=["Timestamp", "Base_Number", "Daily_Number", "Top_Digits"])

def get_latest_base_number(day):
    df = load_day_history(day)
    if not df.empty and "Base_Number" in df.columns:
        latest = df["Base_Number"].iloc[0]
        if validate_number(latest):
            return latest
    return "048808" # ค่าเริ่มต้นถ้ายังไม่มีประวัติ

def save_analysis_history(day, base_number, daily_number, top_digits):
    filename = CSV_FILE_MAP.get(day)
    if not filename:
        return
    
    new_record = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Base_Number": str(base_number),
        "Daily_Number": str(daily_number),
        "Top_Digits": "-".join([str(d) for d in top_digits])
    }
    
    df = load_day_history(day)
    df_new = pd.DataFrame([new_record])
    df = pd.concat([df_new, df], ignore_index=True)
    df.to_csv(filename, index=False, encoding="utf-8-sig")


# =====================================================
# 4. FORMULA ENGINE - 15 FORMULAS
# =====================================================

def validate_number(number):
    return bool(re.fullmatch(r"[0-9]{6}", str(number)))


def formula1(number):
    a, b, c, d, e, f = map(int, number)
    value = ((a+b+c)*(d+e+f) + (a*f) + (c*e)) % 10000
    result = f"{value:04d}"
    return formula5(number) if result == "0000" else result


def formula2(number):
    a, b, c, d, e, f = map(int, number)
    return f"{((a*b)+(c*d)+(e*f)) % 10000:04d}"


def formula3(number):
    digits = list(map(int, number))
    return f"{(sum(digits)*111) % 10000:04d}"


def formula4(number):
    a, b, c, d, e, f = map(int, number)
    value = ((a+b+c)*(d+e+f)) % 10000
    result = f"{value:04d}"
    return formula5(number) if result == "0000" else result


def formula5(number):
    digits = list(map(int, number))
    score = Counter()
    counter = Counter(digits)

    for digit, count in counter.items():
        score[digit] += count * 5

    for i in range(len(digits)-1):
        score[(digits[i]+digits[i+1]) % 10] += 2

    for i in range(len(digits)-1):
        score[(digits[i]*digits[i+1]) % 10] += 2

    for i in range(len(digits)-1):
        score[abs(digits[i]-digits[i+1])] += 1

    ranking = sorted(score.items(), key=lambda x: (-x[1], x[0]))
    selected = [str(d) for d, _ in ranking[:4]]
    return "".join(selected).zfill(4)


def formula6(number):
    a, b, c, d, e, f = map(int, number)
    return f"{((a+c+e)*(b+d+f)) % 10000:04d}"


def formula7(number):
    a, b, c, d, e, f = map(int, number)
    return f"{((a*10+b)+(e*10+f)) % 10000:04d}"


def formula8(number):
    digits = list(map(int, number))
    return f"{(sum(digits)*123) % 10000:04d}"


def formula9(number):
    a, b, c, d, e, f = map(int, number)
    front = a*100+b*10+c
    back = d*100+e*10+f
    return f"{abs(front-back) % 10000:04d}"


def formula10(number):
    a, b, c, d, e, f = map(int, number)
    return f"{((a*f)+(b*e)+(c*d)) % 10000:04d}"


def formula11(number):
    digits = list(map(int, number))
    results = []
    for i in range(len(digits)):
        for j in range(i+1, len(digits)):
            results.append(f"{(digits[i]*digits[j]) % 100:02d}")

    counter = Counter(results)
    ranking = sorted(counter.items(), key=lambda x: (-x[1], int(x[0])))

    if not ranking:
        return "0000"
    if len(ranking) == 1:
        return ranking[0][0] * 2

    return ranking[0][0] + ranking[1][0]


def formula12(number):
    _, _, _, d, e, _ = map(int, number)
    base = (d+e) % 10
    return "".join(str((base+i) % 10) for i in range(4))


def formula13(number):
    a, _, c, _, _, f = map(int, number)
    return f"{((a+c+f)*9) % 10000:04d}"


def formula14(number):
    f = int(number[5])
    return f"{f}{f}{(f+1)%10}{(f+1)%10}"


def formula_neighbor(number):
    pos4 = int(number[3])
    pos6 = int(number[5])
    front = (pos6-1) % 10
    back = (pos4+2) % 10
    return f"{front}{back}{(back+1)%10}{(back+2)%10}"


FORMULAS = [
    ("Formula 1", formula1),
    ("Formula 2", formula2),
    ("Formula 3", formula3),
    ("Formula 4", formula4),
    ("Formula 5", formula5),
    ("Formula 6", formula6),
    ("Formula 7", formula7),
    ("Formula 8", formula8),
    ("Formula 9", formula9),
    ("Formula 10", formula10),
    ("Formula 11", formula11),
    ("Formula 12", formula12),
    ("Formula 13", formula13),
    ("Formula 14", formula14),
    ("Formula 15 - Neighbor", formula_neighbor)
]


# =====================================================
# 5. FORMULA CALCULATION
# =====================================================

def calculate_all_formulas(base_number):
    outputs = {}
    errors = {}

    for name, function in FORMULAS:
        try:
            result = str(function(base_number)).strip()
            if not re.fullmatch(r"[0-9]{1,4}", result):
                raise ValueError(f"Invalid formula output: {result}")
            outputs[name] = result.zfill(4)
        except Exception as error:
            errors[name] = str(error)

    return outputs, errors


# =====================================================
# 6. HYBRID FREQUENCY ENGINE
# =====================================================

def calculate_frequency(formula_outputs, daily_number):
    formula_counter = Counter()
    daily_counter = Counter()

    for result in formula_outputs.values():
        if re.fullmatch(r"[0-9]{4}", result):
            formula_counter.update(result)

    if re.fullmatch(r"[0-9]+", daily_number):
        daily_counter.update(daily_number)

    combined_counter = formula_counter + daily_counter

    ranking = sorted(
        combined_counter.items(),
        key=lambda x: (-x[1], int(x[0]))
    )

    return (
        formula_counter,
        daily_counter,
        combined_counter,
        ranking
    )


# =====================================================
# 7. PERMUTATION ENGINE (สลับตำแหน่งทั้งหมด)
# =====================================================

def generate_combinations(digits, length, include_reverse=True):
    if len(digits) < length:
        return []

    results = []

    # ใช้ permutations เพื่อสร้างเลขสลับตำแหน่งทุกรูปแบบ
    for group in permutations(digits, length):
        number = "".join(group)
        results.append(number)

        if include_reverse:
            reverse_number = number[::-1]
            if reverse_number != number:
                results.append(reverse_number)

    return list(dict.fromkeys(results))


# =====================================================
# 8. DISPLAY HELPERS
# =====================================================

def display_number_cards(ranking, formula_counter, daily_counter):
    html = ['<div class="grid-container">']

    for digit, total in ranking:
        formula_count = formula_counter[digit]
        daily_count = daily_counter[digit]

        html.append(
            f'<div class="stat-card">'
            f'<div class="stat-num">{digit}</div>'
            f'<div class="stat-count">{total} ครั้ง</div>'
            f'<div style="font-size:10px;color:#64748b;margin-top:5px;">'
            f'สูตร {formula_count} + Daily {daily_count}'
            f'</div></div>'
        )

    html.append('</div>')
    st.html("".join(html))


def display_number_group(title, numbers):
    if not numbers:
        st.info(f"{title}: ไม่มีชุดตัวเลข")
        return

    badges = "".join(
        f'<span class="badge-number">{number}</span>'
        for number in numbers
    )

    st.markdown(f"""
    <div class="pair-box">
        <div class="pair-title">
            {title} ({len(numbers)} ชุด)
        </div>
        {badges}
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# 9. MAIN STREAMLIT INTERFACE
# =====================================================

st.title("🧠 LAO AI PROFESSIONAL")
st.caption(f"{VERSION} | {len(FORMULAS)} Formula Engines")
st.markdown("---")

# -----------------------------------------------------
# Daily Number Selection (5 Days Only)
# -----------------------------------------------------

st.subheader("📅 Daily Number Engine & Day Selection")

day_options = list(DAILY_NUMBERS.keys())
default_index = day_options.index(DEFAULT_DAY)

selected_day = st.selectbox(
    "เลือกวันสำหรับวิเคราะห์ (จันทร์ - ศุกร์)",
    day_options,
    index=default_index,
    format_func=lambda x: DAY_NAMES_TH[x]
)

daily_number = get_daily_number(selected_day)
latest_base = get_latest_base_number(selected_day)

st.info(
    f"Daily Number: **{daily_number}** | "
    f"ประจำ{DAY_NAMES_TH[selected_day]} | "
    f"ไฟล์ประวัติ: `{CSV_FILE_MAP[selected_day]}`"
)

# -----------------------------------------------------
# Base Number
# -----------------------------------------------------

st.subheader("🔢 เลขฐาน")

base_input = st.text_input(
    f"ป้อนเลขฐาน 6 หลัก (ดึงค่าล่าสุดของ{DAY_NAMES_TH[selected_day]}ให้อัตโนมัติ)",
    value=latest_base,
    max_chars=6,
    placeholder="เช่น 048808"
)

# -----------------------------------------------------
# Display Settings
# -----------------------------------------------------

st.subheader("⚙️ Analysis Settings")

display_count = st.radio(
    "จำนวนเลขเด่นที่ต้องการแสดง",
    [5, 6],
    index=1,
    horizontal=True
)

include_reverse = st.checkbox(
    "เปิดใช้งานเลขกลับ (Permutation Engine)",
    value=True
)

# -----------------------------------------------------
# Run Analysis
# -----------------------------------------------------

if st.button("🚀 ANALYZE LAO LOTTERY", type="primary", use_container_width=True):

    if not validate_number(base_input):
        st.error("กรุณากรอกเลขฐานให้ครบ 6 หลัก และใช้ตัวเลข 0-9 เท่านั้น")
    else:
        # A. FORMULA ENGINE
        outputs, errors = calculate_all_formulas(base_input)

        # B. HYBRID FREQUENCY ENGINE
        (
            formula_counter,
            daily_counter,
            combined_counter,
            ranking
        ) = calculate_frequency(outputs, daily_number)

        top_digits = ranking[:display_count]
        digits_only = [digit for digit, count in top_digits]

        # บันทึกประวัติลง CSV ประจำวันนั้นๆ อัตโนมัติ
        save_analysis_history(selected_day, base_input, daily_number, digits_only)

        # C. SUMMARY
        st.markdown("---")
        st.header("📊 ANALYSIS REPORT")
        st.success(f"วิเคราะห์และบันทึกลง `{CSV_FILE_MAP[selected_day]}` เรียบร้อยแล้ว")

        col1, col2, col3 = st.columns(3)
        col1.metric("สูตรสำเร็จ", f"{len(outputs)}/15")
        col2.metric("จำนวนหลักจากสูตร", len(outputs)*4)
        col3.metric("Daily Number", len(daily_number))

        if errors:
            st.warning(f"พบสูตรผิดพลาด {len(errors)} สูตร")
            for name, error in errors.items():
                st.error(f"{name}: {error}")

        # D. FORMULA OUTPUT TABLE
        st.subheader("1. ผลลัพธ์จาก 15 สูตร")
        formula_rows = [{"Formula": name, "Result": result} for name, result in outputs.items()]
        st.dataframe(formula_rows, use_container_width=True, hide_index=True)

        # E. DAILY NUMBER
        st.subheader("2. Daily Number")
        st.markdown(f"""
        <div class="pair-box">
            <div class="pair-title">{DAY_NAMES_TH[selected_day]}</div>
            <span class="badge-number badge-highlight">{daily_number}</span>
        </div>
        """, unsafe_allow_html=True)

        # F. HYBRID DIGIT FREQUENCY
        st.subheader("3. เลขที่ปรากฏบ่อยจาก 15 สูตร + Daily Number")
        display_number_cards(top_digits, formula_counter, daily_counter)

        total_digits = len(outputs)*4 + len(daily_number)
        st.caption(
            f"รวมจำนวนหลักที่นำมาวิเคราะห์: {total_digits} หลัก "
            f"({len(outputs)*4} หลักจากสูตร + {len(daily_number)} หลักจาก Daily Number)"
        )

        # G. FULL FREQUENCY TABLE
        with st.expander("ดูความถี่เลข 0-9 ทั้งหมด"):
            frequency_rows = []
            for digit in range(10):
                key = str(digit)
                frequency_rows.append({
                    "เลข": key,
                    "Formula Frequency": formula_counter[key],
                    "Daily Frequency": daily_counter[key],
                    "Total Frequency": combined_counter[key]
                })

            frequency_rows.sort(key=lambda x: (-x["Total Frequency"], int(x["เลข"])))
            st.dataframe(frequency_rows, use_container_width=True, hide_index=True)

        # H. TOP NUMBER GROUPS
        st.markdown("---")
        st.subheader("4. เลขเด่นจากการจัดอันดับ")
        main_group = digits_only[:3]
        secondary_group = digits_only[3:6]
        remaining_group = [str(i) for i in range(10) if str(i) not in digits_only]

        st.write("**กลุ่มเด่น:** " + " - ".join(main_group))
        st.write("**กลุ่มรอง:** " + (" - ".join(secondary_group) if secondary_group else "-"))
        st.write("**เลขอื่น ๆ:** " + (" - ".join(remaining_group) if remaining_group else "-"))

        # I. SPECIAL TOP PICKS
        st.markdown("---")
        st.subheader("5. TOP PICKS")
        if len(digits_only) >= 3:
            top_3 = "".join(digits_only[:3])
            top_2 = "".join(digits_only[:2])
            st.markdown(f"""
            <div class="pair-box">
                <div class="pair-title">⭐ ชุดเน้นพิเศษ</div>
                <span class="badge-number badge-highlight">3 ตัว: {top_3}</span>
                <span class="badge-number badge-highlight">2 ตัว: {top_2}</span>
            </div>
            """, unsafe_allow_html=True)

        # J. COMBINATION ENGINE (PERMUTATIONS)
        st.markdown("---")
        st.header("🎯 COMBINATION & PERMUTATION ENGINE")
        st.caption("สร้างชุดและสลับตำแหน่งตัวเลขทั้งหมดจากเลขเด่นที่จัดอันดับ")

        lengths = [5, 4, 3, 2]
        for length in lengths:
            generated = generate_combinations(digits_only, length, include_reverse)
            display_number_group(f"🎲 ชุด {length} ตัว (สลับตำแหน่ง)", generated)

        # K. HISTORY TABLE FOR SELECTED DAY
        st.markdown("---")
        st.subheader(f"📜 ประวัติการวิเคราะห์ ({DAY_NAMES_TH[selected_day]})")
        df_hist = load_day_history(selected_day)
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("ยังไม่มีประวัติการบันทึกสำหรับวันนี้")

        # L. FINAL SUMMARY
        st.markdown("---")
        st.subheader("6. FINAL SUMMARY")
        st.write(f"**เลขฐาน:** {base_input}")
        st.write(f"**วันวิเคราะห์:** {DAY_NAMES_TH[selected_day]}")
        st.write(f"**Daily Number:** {daily_number}")
        st.write("**เลขเด่น:** " + " - ".join(digits_only))
        st.write(f"**จำนวนสูตรที่สำเร็จ:** {len(outputs)}/15")
        st.write(f"**ไฟล์ประวัติที่อัปเดต:** `{CSV_FILE_MAP[selected_day]}`")
        st.caption("หมายเหตุ: ระบบนี้เป็นเครื่องมือวิเคราะห์ความถี่และความสัมพันธ์ของตัวเลข ไม่ใช่การรับประกันผลรางวัล")

else:
    st.markdown("---")
    # แสดงประวัติของวันที่เลือกในหน้าแรก
    st.subheader(f"📜 ประวัติล่าสุดประจำ{DAY_NAMES_TH[selected_day]}")
    df_hist = load_day_history(selected_day)
    if not df_hist.empty:
        st.dataframe(df_hist.head(5), use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีประวัติการบันทึกสำหรับวันนี้")

    st.caption("LAO AI PROFESSIONAL v4.1 (5-Day CSV System)")
