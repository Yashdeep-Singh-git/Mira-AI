import streamlit as st
from mira_sdk import MiraClient, Flow
from dotenv import load_dotenv
import os
from typing import Dict, Union
import json
import pandas as pd

# Previous DietPlannerClient class remains exactly the same
class DietPlannerClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            raise ValueError("API_KEY not found in environment variables")
        self.client = MiraClient(config={"API_KEY": self.api_key})
        
    def validate_input(self, data: Dict[str, str]) -> Dict[str, str]:
        required_fields = ["Age", "Goal", "Gender", "Height", "Weight"]
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"{field} is required")
        try:
            age = int(data["Age"])
            if not (0 < age < 120):
                raise ValueError("Age must be between 1 and 120")
            weight = float(data["Weight"])
            if not (20 < weight < 500):
                raise ValueError("Weight must be between 20 and 500")
            height = float(data["Height"])
            if not (50 < height < 300):
                raise ValueError("Height must be between 50 and 300")
        except ValueError as e:
            raise ValueError(f"Invalid input: {str(e)}")
        return data

    def get_diet_plan(self, input_data: Dict[str, str], version: str = "1.0.0") -> Dict:
        try:
            validated_data = self.validate_input(input_data)
            flow_name = f"@mystery2000/advanced-diet-planner-/{version}"
            result = self.client.flow.execute(flow_name, validated_data)
            return result
        except Exception as e:
            raise Exception(f"Error getting diet plan: {str(e)}")

def format_diet_plan_for_txt(diet_plan: Dict) -> str:
    """Format the diet plan data for text file output"""
    txt_content = "YOUR PERSONALIZED DIET PLAN\n"
    txt_content += "=" * 30 + "\n\n"
    
    # Add the main diet plan content
    txt_content += diet_plan['result']
    
    return txt_content

def main():
    # Page config must be the first Streamlit command
    st.set_page_config(
        page_title="Advanced Diet Planner",
        page_icon="🥗",
        layout="wide"
    )

    # Previous CSS styling remains the same
    st.markdown("""
        <style>
        /* Main background and text styles */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Header styles */
        h1 {
            color: #2c3e50;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
            text-align: center;
            padding: 1.5rem 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Subheader styles */
        h2, h3 {
            color: #34495e;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 600;
            margin-top: 1rem;
        }
        
        /* Form container styles */
        .stForm {
            background-color: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Input field styles */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 0.5rem;
            font-family: 'Arial', sans-serif;
        }
        
        /* Button styles */
        .stButton > button {
            background: linear-gradient(45deg, #2ecc71, #27ae60);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Success message styles */
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            text-align: center;
        }
        
        /* Diet plan result container */
        .diet-plan-container {
            background-color: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }
        
        /* Download button container */
        .download-container {
            text-align: center;
            margin-top: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Rest of the UI code remains the same
    st.markdown("<h1>🥗 Advanced Diet Planner</h1>", unsafe_allow_html=True)
    st.markdown("""
        <p style='text-align: center; font-size: 1.2em; color: #555; margin-bottom: 2rem;'>
            Create your personalized diet plan based on your goals and preferences
        </p>
    """, unsafe_allow_html=True)

    if 'diet_plan' not in st.session_state:
        st.session_state.diet_plan = None

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 👤 Personal Information")
            age = st.number_input("Age", min_value=1, max_value=120, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            height = st.number_input("Height (cm)", min_value=50, max_value=300, step=1)
            weight = st.number_input("Weight (kg)", min_value=20, max_value=500, step=1)
            veg_nonveg = st.selectbox("Dietary Preference", ["VEG", "NON-VEG"])

        with col2:
            st.markdown("### 🎯 Goals & Health Information")
            goal = st.selectbox("Goal", [
                "Weight Loss",
                "Muscle Gain",
                "Maintenance",
                "General Health"
            ])
            food_allergies = st.text_area("Food Allergies", placeholder="Enter any food allergies (if none, leave blank)")
            medical_conditions = st.text_area("Medical Conditions", placeholder="Enter any medical conditions (if none, leave blank)")
            
            if food_allergies == "":
                food_allergies = "None"
            if medical_conditions == "":
                medical_conditions = "None"

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("✨ Generate My Diet Plan", type="primary"):
            try:
                with st.spinner("🔄 Creating your personalized diet plan..."):
                    input_data = {
                        "Age": str(age),
                        "Goal": goal,
                        "Gender": gender,
                        "Height": str(height),
                        "Weight": str(weight),
                        "Veg/Non-Veg": veg_nonveg,
                        "Food Allergy": food_allergies,
                        "Medical Condition": medical_conditions
                    }

                    planner = DietPlannerClient()
                    result = planner.get_diet_plan(input_data)
                    st.session_state.diet_plan = result

            except Exception as e:
                st.error(f"⚠️ Error: {str(e)}")
                return

    if st.session_state.diet_plan:
        st.markdown("""
            <div class='success-message'>
                ✨ Your personalized diet plan has been generated successfully!
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### 📋 Your Diet Plan")
            st.markdown("""
                <div class='diet-plan-container'>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.diet_plan['result'])
            st.markdown("</div>", unsafe_allow_html=True)

        # Modified download button to save as .txt
        st.markdown("<div class='download-container'>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Download Diet Plan",
            data=format_diet_plan_for_txt(st.session_state.diet_plan),
            file_name="diet_plan.txt",
            mime="text/plain"
        )
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()