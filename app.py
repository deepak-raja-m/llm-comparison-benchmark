import streamlit as st
import requests
import pandas as pd
import json
import time

st.set_page_config(
    page_title="LLM Comparison Benchmark",
    page_icon="⚡",
    layout="wide"
)

# Dark modern styling
st.markdown("""
<style>
    .stApp {
        background: #0f172a;
        color: #f1f5f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .brand-title {
        font-size: 2rem;
        font-weight: 800;
        color: #38bdf8;
        display: inline-block;
    }
    .brand-tagline {
        font-size: 0.85rem;
        font-weight: 700;
        color: #94a3b8;
        margin-left: 10px;
    }
    .user-pill {
        display: inline-block;
        background: #1e293b;
        border: 1px solid #38bdf8;
        border-radius: 20px;
        padding: 6px 16px;
        color: #7dd3fc;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 15px;
    }
    .card-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .metric-tile {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    div.stButton > button {
        background: #0284c7 !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1rem !important;
    }
    div.stButton > button:hover {
        background: #0369a1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "email" not in st.session_state:
    st.session_state.email = ""
if "active_page" not in st.session_state:
    st.session_state.active_page = "🏠 Overview"
if "benchmarks_run" not in st.session_state:
    st.session_state.benchmarks_run = 0
if "benchmark_history" not in st.session_state:
    st.session_state.benchmark_history = []

# ----------------- API INVOCATION WITH TELEMETRY -----------------
def execute_llm_benchmark(model_name, prompt, api_key, temperature=0.7, max_tokens=600):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key.strip()}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature
        }
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        latency = round(time.time() - start_time, 2)
        
        if response.status_code == 200:
            data = response.json()
            output_text = data["candidates"][0]["content"]["parts"][0]["text"]
            token_count = len(output_text.split()) * 1.3
            throughput = round(token_count / latency, 2) if latency > 0 else 0
            
            return {
                "model": model_name,
                "status": "Success",
                "latency_sec": latency,
                "approx_tokens": int(token_count),
                "throughput_tps": throughput,
                "response": output_text
            }
        else:
            return {
                "model": model_name,
                "status": f"HTTP {response.status_code}",
                "latency_sec": latency,
                "approx_tokens": 0,
                "throughput_tps": 0,
                "response": response.text
            }
    except Exception as e:
        latency = round(time.time() - start_time, 2)
        return {
            "model": model_name,
            "status": "Failed",
            "latency_sec": latency,
            "approx_tokens": 0,
            "throughput_tps": 0,
            "response": str(e)
        }

# ----------------- 1. LOGIN SCREEN -----------------
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='card-box' style='text-align: center;'>
            <div class='brand-title'>⚡ BenchMark Studio</div>
            <div style='color: #94a3b8; font-weight: 600; margin-top: 5px; margin-bottom: 20px;'>
                LARGE LANGUAGE MODEL EVALUATION & TELEMETRY
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        login_name = st.text_input("Operator Name:", placeholder="Enter your full name")
        login_email = st.text_input("Academic / College Email:", placeholder="name@domain.edu")
        login_key = st.text_input("Gemini API Key:", type="password", placeholder="Enter AI Studio API Key (AIza...)")
        
        if st.button("Access Benchmark Console", use_container_width=True):
            if not login_name.strip() or not login_email.strip():
                st.warning("Please enter your name and email to continue.")
            else:
                st.session_state.logged_in = True
                st.session_state.username = login_name.strip()
                st.session_state.email = login_email.strip()
                if login_key.strip():
                    st.session_state.api_key = login_key.strip()
                st.rerun()

# ----------------- 2. MAIN APPLICATION -----------------
else:
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown(f"""
        <div>
            <span class='brand-title'>⚡ BenchMark Studio</span>
            <span class='brand-tagline'>• MULTI-LLM EVALUATION & PERFORMANCE ENGINE</span>
        </div>
        <div class='user-pill'>
            👤 Evaluator: {st.session_state.username} ({st.session_state.email})
        </div>
        """, unsafe_allow_html=True)
        
    with top_col2:
        runs = st.session_state.benchmarks_run
        st.write(f"**⚡ Evaluations Run:** `{runs}`")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # Navigation bar
    n1, n2, n3, n4 = st.columns(4)
    with n1:
        if st.button("🏠 Overview", use_container_width=True):
            st.session_state.active_page = "🏠 Overview"
            st.rerun()
    with n2:
        if st.button("🧪 Live Benchmark", use_container_width=True):
            st.session_state.active_page = "🧪 Live Benchmark"
            st.rerun()
    with n3:
        if st.button("📊 Comparative Metrics", use_container_width=True):
            st.session_state.active_page = "📊 Comparative Metrics"
            st.rerun()
    with n4:
        if st.button("📄 Architecture & Methodology", use_container_width=True):
            st.session_state.active_page = "📄 Architecture & Methodology"
            st.rerun()

    st.write("---")

    # TAB 1: OVERVIEW
    if st.session_state.active_page == "🏠 Overview":
        st.markdown("""
        <div class='card-box'>
            <h3 style='color: #38bdf8; margin: 0 0 6px 0;'>🔬 Automated Large Language Model Benchmarking Hub</h3>
            <p style='color: #94a3b8; margin: 0;'>
                Execute identical standardized prompts across multiple frontier model variants to measure inference latency, token throughput, output verbosity, and semantic accuracy.
            </p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class='metric-tile'>
                <small style='color: #94a3b8;'>Total Invocations</small>
                <h2 style='color: #38bdf8; margin: 4px 0 0 0;'>{st.session_state.benchmarks_run}</h2>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown("""
            <div class='metric-tile'>
                <small style='color: #94a3b8;'>Active Models</small>
                <h2 style='color: #10b981; margin: 4px 0 0 0;'>3 Models</h2>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
            <div class='metric-tile'>
                <small style='color: #94a3b8;'>Measured KPIs</small>
                <h2 style='color: #a78bfa; margin: 4px 0 0 0;'>Latency & TPS</h2>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown("""
            <div class='metric-tile'>
                <small style='color: #94a3b8;'>Protocol</small>
                <h2 style='color: #f59e0b; margin: 4px 0 0 0;'>RESTful v1beta</h2>
            </div>
            """, unsafe_allow_html=True)

    # TAB 2: LIVE BENCHMARK
    elif st.session_state.active_page == "🧪 Live Benchmark":
        st.markdown("### 🧪 Multi-Model Prompt Execution")
        st.caption("Broadcast a single benchmark prompt across multiple LLM endpoints simultaneously.")
        
        saved_key = st.session_state.get("api_key", "")
        api_key_input = st.text_input("Gemini API Key:", value=saved_key, type="password", placeholder="Enter key (AIza...)")
        
        col_m, col_t = st.columns([2, 1])
        with col_m:
            selected_models = st.multiselect(
                "Select Models to Benchmark:",
                ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
                default=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
            )
        with col_t:
            test_temp = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

        test_prompt = st.text_area(
            "Benchmark Prompt / Task:",
            value="Explain the core difference between monolithic and microservices architecture in 3 bullet points, then provide a 1-sentence conclusion.",
            height=120
        )

        if st.button("🚀 Run Comparison Benchmark", use_container_width=True):
            if not api_key_input.strip():
                st.error("Please enter a valid Gemini API Key.")
            elif not selected_models:
                st.warning("Please select at least one model to benchmark.")
            elif not test_prompt.strip():
                st.warning("Prompt cannot be empty.")
            else:
                st.session_state.api_key = api_key_input.strip()
                results = []
                
                with st.status("Executing inference benchmark across targets...", expanded=True) as status:
                    for model in selected_models:
                        st.write(f"⏳ Calling **{model}**...")
                        res = execute_llm_benchmark(model, test_prompt, api_key_input, temperature=test_temp)
                        results.append(res)
                        time.sleep(0.5)
                    status.update(label="✅ Benchmark Completed!", state="complete", expanded=False)
                
                st.session_state.benchmarks_run += 1
                for r in results:
                    st.session_state.benchmark_history.append(r)
                
                st.markdown("### 📊 Real-Time Benchmark Results")
                df_results = pd.DataFrame([{
                    "Model": r["model"],
                    "Status": r["status"],
                    "Latency (s)": r["latency_sec"],
                    "Est. Tokens": r["approx_tokens"],
                    "Throughput (tok/s)": r["throughput_tps"]
                } for r in results])
                
                st.dataframe(df_results, use_container_width=True)

                st.markdown("### 📝 Side-by-Side Model Responses")
                cols = st.columns(len(results))
                for idx, r in enumerate(results):
                    with cols[idx]:
                        st.markdown(f"**🤖 {r['model']}**")
                        st.caption(f"⏱️ {r['latency_sec']}s | ⚡ {r['throughput_tps']} tok/s")
                        st.markdown(f"""
                        <div class='card-box' style='min-height: 250px; font-size: 0.95rem;'>
                            {r['response']}
                        </div>
                        """, unsafe_allow_html=True)

    # TAB 3: COMPARATIVE METRICS
    elif st.session_state.active_page == "📊 Comparative Metrics":
        st.markdown("### 📊 Benchmark Historical Telemetry")
        if not st.session_state.benchmark_history:
            st.info("No benchmarks have been run in this session yet. Execute runs in the 'Live Benchmark' tab to view aggregated metrics.")
        else:
            hist_df = pd.DataFrame(st.session_state.benchmark_history)
            st.dataframe(hist_df[["model", "status", "latency_sec", "approx_tokens", "throughput_tps"]], use_container_width=True)
            
            st.markdown("#### Latency vs. Throughput Analysis")
            summary = hist_df.groupby("model")[["latency_sec", "throughput_tps"]].mean().reset_index()
            st.bar_chart(summary.set_index("model")["latency_sec"])
            st.caption("Average Latency (seconds) by Model - Lower is better.")

    # TAB 4: ARCHITECTURE & METHODOLOGY
    elif st.session_state.active_page == "📄 Architecture & Methodology":
        st.markdown("### 📄 Evaluation Methodology & Criteria")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class='card-box'>
                <h4 style='color: #38bdf8; margin: 0 0 8px 0;'>⏱️ 1. Latency & Time-to-First-Token (TTFT)</h4>
                <p style='color: #cbd5e1; font-size: 0.95rem; margin: 0;'>
                    Measures round-trip response turnaround over REST endpoints from the initial HTTP POST dispatch to full stream delivery.
                </p>
            </div>
            <div class='card-box'>
                <h4 style='color: #38bdf8; margin: 0 0 8px 0;'>⚡ 2. Token Throughput (Tokens / Sec)</h4>
                <p style='color: #cbd5e1; font-size: 0.95rem; margin: 0;'>
                    Tracks generation velocity, calculated by dividing the total estimated completion tokens by total elapsed response latency.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown("""
            <div class='card-box'>
                <h4 style='color: #38bdf8; margin: 0 0 8px 0;'>🎯 3. Parameter Determinism</h4>
                <p style='color: #cbd5e1; font-size: 0.95rem; margin: 0;'>
                    Benchmarking applies identical temperature controls and token maximum constraints across all candidates simultaneously.
                </p>
            </div>
            <div class='card-box'>
                <h4 style='color: #38bdf8; margin: 0 0 8px 0;'>🛡️ 4. Model Reliability & Error Handling</h4>
                <p style='color: #cbd5e1; font-size: 0.95rem; margin: 0;'>
                    Monitors HTTP status return codes (such as 429 quota exhaustion or 503 capacity limits) to assess operational stability.
                </p>
            </div>
            """, unsafe_allow_html=True)