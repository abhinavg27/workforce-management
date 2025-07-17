import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import os
import openai
import httpx # Still needed for httpx.Client and httpx.HTTPTransport
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# --- Flask App Setup ---
app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
CORS(app)

# --- OpenAI API Configuration ---
RAKUTEN_OPENAI_API_KEY = "raik-sk-adf42e626r10aie9a6598cad9c615e1cfd340dec18b64be9a6598cad9c615e1c"
RAKUTEN_OPENAI_BASE_URL = "https://api.ai.public.rakuten-it.com/openai/v1/"

# --- FINAL ATTEMPT AT PROXY FIX: Explicitly define an httpx Transport without proxies ---
try:
    # Create a transport that explicitly states no proxies
    transport = httpx.HTTPTransport(
        proxy=None, # Explicitly no proxy for the transport
        verify=True, # Standard SSL verification
    )
    # Create an httpx.Client using this transport
    httpx_client_instance = httpx.Client(
        transport=transport,
    )
    # Initialize the OpenAI client with this pre-configured httpx Client
    client = openai.OpenAI(
        api_key=RAKUTEN_OPENAI_API_KEY,
        base_url=RAKUTEN_OPENAI_BASE_URL,
        http_client=httpx_client_instance, # Pass the configured httpx client
    )
    print("OpenAI client initialized with explicit no-proxy HTTPTransport.")
except Exception as e:
    print(f"Failed to initialize OpenAI client with explicit no-proxy: {e}")
    print("Attempting to initialize OpenAI client without explicit httpx config (may still encounter proxy issues).")
    # Fallback initialization if the explicit transport method also fails
    client = openai.OpenAI(
        api_key=RAKUTEN_OPENAI_API_KEY,
        base_url=RAKUTEN_OPENAI_BASE_URL,
    )

print(f"OpenAI API Key (first 10 chars): {client.api_key[:10]}...")
print(f"OpenAI Base URL: {client.base_url}")
print("-" * 50)

# --- Data Loading or Generation ---
def load_or_generate_historical_data(csv_path='data/historical_supersale_data.csv', num_events=12):
    try:
        print(f"Attempting to load historical data from {csv_path}...")
        df = pd.read_csv(csv_path)
        df['Supersale_Date'] = pd.to_datetime(df['Supersale_Date'])
        
        numeric_cols_float = [
            'Total_Volume_Shipped_CBM', 'Total_Weight_Shipped_KG', 
            'Average_Order_Size_Units', 'Customer_Satisfaction_Score', 
            'Average_Processing_Time_Per_Order_Seconds', 'Total_Labor_Hours_Actual'
        ]
        numeric_cols_int = [
            'Total_Orders_Processed', 'Total_SKUs_Processed', 'Peak_Hour_Order_Rate',
            'Number_of_Workers_Deployed_Actual'
        ]

        # Dynamically add task-specific labor hours and units processed to numeric columns
        for col in df.columns:
            if col.endswith('_Labor_Hours_Actual') and col not in numeric_cols_float:
                numeric_cols_float.append(col)
            elif col.endswith('_Units_Processed') and col not in numeric_cols_int:
                numeric_cols_int.append(col)

        for col in numeric_cols_float:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        for col in numeric_cols_int:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        required_cols = ['Total_Orders_Processed', 'Total_Labor_Hours_Actual', 'Supersale_Date']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            raise ValueError(f"CSV is missing one or more required columns: {missing}. Please check your CSV header.")

        print(f"Successfully loaded {len(df)} historical records from {csv_path}.")
        return df

    except FileNotFoundError:
        print(f"CSV file not found at {csv_path}. Generating synthetic data instead.")
        return generate_synthetic_supersale_data(num_events)
    except Exception as e:
        print(f"Error loading historical data from CSV: {e}. Generating synthetic data instead.")
        return generate_synthetic_supersale_data(num_events)

# --- Synthetic Data Generation (Fallback) ---
def generate_synthetic_supersale_data(num_events=12):
    """
    Generates a synthetic dataset for Supersale events.
    Reflects growth over time and plausible correlations.
    Ensures non-zero orders and labor hours for model training.
    Introduces more randomness in task-specific labor hours.
    """
    print("Generating synthetic data with varied task hours...")
    data = []
    start_date = datetime(2022, 7, 15)
    base_orders = 150000
    order_growth_per_year = 1.07
    efficiency_improvement_per_year = 0.99
    
    # Base task proportions (these are just starting points now)
    task_proportions_bases = {
        'Receive': 0.05, 'Stow': 0.075, 'D2B': 0.02, 'Pick_Paperless': 0.20,
        'Pick_Paper': 0.10, 'Induction': 0.04, 'DPS': 0.03, 'Rebin_Manual': 0.02,
        'Rebin_DAS': 0.01, 'Pack': 0.15, 'Gift': 0.01, 'Pick_to_Go_Paperless': 0.02,
        'ShipSort': 0.05, 'Maintenance': 0.015, 'QA': 0.01, 'Forklift': 0.02,
        'Management': 0.03, 'Pack_Return': 0.01, 'Pack_Paperless': 0.05, 
        'Pack_Paper': 0.05, 'Pick_to_Go_Paper': 0.01,
    }
    # Ensure they sum to 1 (initial normalization)
    total_prop_sum = sum(task_proportions_bases.values())
    task_proportions_bases = {k: v / total_prop_sum for k, v in task_proportions_bases.items()}

    for i in range(num_events):
        current_date = start_date + timedelta(days=i * 91)
        year_offset = (current_date - datetime(2022, 1, 1)).days / 365.25

        total_orders = base_orders * (order_growth_per_year ** year_offset) * (1 + np.random.normal(0, 0.05))
        total_orders = int(max(10000, total_orders))

        if current_date.month == 10: # Simulate a bump for October/Q4 sales
            total_orders = int(total_orders * 1.15)
        elif current_date.month in [11, 12]: # Even bigger bump for Nov/Dec
            total_orders = int(total_orders * 1.25)
        elif current_date.month in [1, 2]: # Slight dip for Jan/Feb
            total_orders = int(total_orders * 0.9)


        total_skus = int(total_orders * np.random.uniform(1.8, 2.5))
        avg_order_size = round(np.random.uniform(2.0, 3.5), 1)
        labor_hours_per_order = 0.06 * (efficiency_improvement_per_year ** year_offset)
        total_labor_hours_base = total_orders * labor_hours_per_order # Calculate base total before noise
        total_labor_hours = round(max(100.0, total_labor_hours_base * (1 + np.random.normal(0, 0.08))), 2)

        num_workers_deployed = int(total_labor_hours / 8)
        total_volume_cbm = round(total_orders * avg_order_size * np.random.uniform(0.0008, 0.0012), 2)
        total_weight_kg = round(total_orders * avg_order_size * np.random.uniform(0.04, 0.06), 2)
        peak_hour_order_rate = int(total_orders * np.random.uniform(0.05, 0.07))
        cs_score = round(np.random.uniform(4.0, 4.8) - (total_orders / 2500000), 1)
        cs_score = max(4.0, cs_score)
        avg_processing_time_per_order_seconds = round((total_labor_hours * 3600) / total_orders if total_orders > 0 else 0, 2)
        
        record = {
            'Supersale_Date': current_date.strftime('%Y-%m-%d'),
            'Total_Orders_Processed': total_orders,
            'Total_SKUs_Processed': total_skus,
            'Total_Volume_Shipped_CBM': total_volume_cbm,
            'Total_Weight_KG': total_weight_kg,
            'Average_Order_Size_Units': avg_order_size,
            'Peak_Hour_Order_Rate': peak_hour_order_rate,
            'Number_of_Workers_Deployed_Actual': num_workers_deployed,
            'Total_Labor_Hours_Actual': total_labor_hours, # This is the final, noisy total
            'Customer_Satisfaction_Score': cs_score,
            'Average_Processing_Time_Per_Order_Seconds': avg_processing_time_per_order_seconds,
        }
        
        # Calculate task-specific labor hours with more significant, independent noise
        task_labor_hours_raw = {}
        for task, base_prop in task_proportions_bases.items():
            noise_factor = 1 + np.random.normal(0, 0.15) # Increased noise std dev to 0.15 (15%)
            task_labor_hours_raw[task] = (total_labor_hours_base * base_prop * noise_factor) # Use base total for initial distribution

        # Now, scale these noisy individual task hours to sum up to the final total_labor_hours
        current_sum_task_hours = sum(task_labor_hours_raw.values())
        if current_sum_task_hours > 0:
            scaling_factor = total_labor_hours / current_sum_task_hours
        else:
            scaling_factor = 0 # Avoid division by zero if all task hours are zero

        for task, raw_hours in task_labor_hours_raw.items():
            final_task_hours = round(raw_hours * scaling_factor, 2)
            record[f'{task}_Labor_Hours_Actual'] = max(0.0, final_task_hours) # Ensure no negative hours

            # Add Units_Processed for relevant tasks (simplified logic)
            if task in ['Receive', 'Stow']:
                record[f'{task}_Units_Processed'] = int(total_skus * np.random.uniform(0.9, 1.1))
            elif task.startswith('Pick'):
                record[f'{task}_Units_Processed'] = int(total_orders * np.random.uniform(1.5, 2.5))
            elif task.startswith('Pack'):
                record[f'{task}_Units_Processed'] = int(total_orders * np.random.uniform(0.9, 1.1))
            elif task == 'D2B':
                record[f'{task}_Units_Processed'] = int(total_skus * np.random.uniform(0.1, 0.2))
            elif task == 'DPS':
                record[f'{task}_Units_Processed'] = int(total_orders * np.random.uniform(0.5, 0.7))
            elif task.startswith('Rebin'):
                record[f'{task}_Units_Processed'] = int(total_orders * np.random.uniform(0.3, 0.5))
            elif task == 'ShipSort':
                record[f'{task}_Units_Processed'] = int(total_orders * np.random.uniform(0.9, 1.0))
            elif task.startswith('Pack_Return'):
                record[f'{task}_Units_Processed'] = int(total_orders * np.random.uniform(0.01, 0.03))
            elif task.startswith('Pick_to_Go'):
                record[f'{task}_Units_Processed'] = int(total_orders * np.random.uniform(0.1, 0.2))
        
        data.append(record)

    df = pd.DataFrame(data)
    # Ensure all possible _Units_Processed columns exist, even if 0
    all_possible_units_cols = [f'{t}_Units_Processed' for t in task_proportions_bases.keys()]
    for col in all_possible_units_cols:
        if col not in df.columns:
            df[col] = 0

    print(f"Generated {len(df)} synthetic records with varied task hours.")
    return df

# --- 2. Solution Design (Forecasting Model) ---
class WorkforceForecaster:
    def __init__(self, historical_df):
        # Store the original, complete historical data
        self.original_historical_df = historical_df.copy()
        
        # Ensure 'Supersale_Date' is datetime and add ordinal and month for filtering
        if not pd.api.types.is_datetime64_any_dtype(self.original_historical_df['Supersale_Date']):
            self.original_historical_df['Supersale_Date'] = pd.to_datetime(self.original_historical_df['Supersale_Date'])
        self.original_historical_df['Supersale_Date_Ordinal'] = self.original_historical_df['Supersale_Date'].apply(lambda date: date.toordinal())
        self.original_historical_df['Month'] = self.original_historical_df['Supersale_Date'].dt.month

        # These will be set dynamically within the forecast method
        self.model = None
        self.task_proportions = {}
        self.mean_abs_error_historical = 0 
        self.feature_cols = ['Total_Orders_Processed', 'Supersale_Date_Ordinal'] # Only these features for the month-specific model

    def _prepare_data_for_training(self, df_to_use):
        """
        Prepares the (potentially filtered) DataFrame for model training.
        This method is now called dynamically with the relevant subset of data.
        """
        # Recalculate Orders_Per_Labor_Hour for the given subset
        df_to_use['Orders_Per_Labor_Hour'] = df_to_use.apply(
            lambda row: row['Total_Orders_Processed'] / row['Total_Labor_Hours_Actual'] if row['Total_Labor_Hours_Actual'] > 0 else 0,
            axis=1
        )
        return df_to_use

    def _train_model(self, filtered_historical_df):
        """
        Trains the linear regression model on the provided (month-specific) historical data.
        """
        self.model = None # Reset model before training
        self.mean_abs_error_historical = 0 # Reset MAE

        if len(filtered_historical_df) < 2:
            print(f"Not enough historical data ({len(filtered_historical_df)} records) for the specific month to train model. Using simple average fallback.")
            return

        X = filtered_historical_df[self.feature_cols]
        y = filtered_historical_df['Total_Labor_Hours_Actual']

        # Check for constant features or target
        if X.empty or y.empty or y.nunique() < 2:
            print(f"Target variable is constant or no features available for the specific month. Linear regression cannot be trained meaningfully. Using simple average fallback.")
            return
        
        # Check if all features are constant
        if all(X[col].nunique() < 2 for col in X.columns):
            print(f"All features are constant for the specific month. Linear regression cannot be trained meaningfully. Using simple average fallback.")
            return

        self.model = LinearRegression()
        self.model.fit(X, y) 
        y_pred = self.model.predict(X)
        self.mean_abs_error_historical = np.mean(np.abs(y - y_pred))
        print(f"Model trained for this month with features: {self.feature_cols}. MAE on historical data: {self.mean_abs_error_historical:.2f}")

    def _calculate_task_proportions(self, filtered_historical_df):
        """
        Calculates task proportions based on the provided (month-specific) historical data.
        """
        task_cols = [col for col in filtered_historical_df.columns if col.endswith('_Labor_Hours_Actual') and col != 'Total_Labor_Hours_Actual']
        if not task_cols:
            print("No task-specific labor hour columns found in filtered historical data. Task allocation will not be available.")
            self.task_proportions = {}
            return

        event_proportions = {}
        for task_col in task_cols:
            task_name = task_col.replace('_Labor_Hours_Actual', '')
            event_proportions[task_name] = []
            for index, row in filtered_historical_df.iterrows():
                total_labor = row['Total_Labor_Hours_Actual']
                task_labor = row[task_col]
                if total_labor > 0:
                    event_proportions[task_name].append(task_labor / total_labor)
                else:
                    event_proportions[task_name].append(0.0) 
        
        self.task_proportions = {}
        for task_name, proportions_list in event_proportions.items():
            if proportions_list:
                self.task_proportions[task_name] = np.mean(proportions_list)
            else:
                self.task_proportions[task_name] = 0.0

        total_sum = sum(self.task_proportions.values())
        if total_sum == 0: 
            print("Warning: Sum of calculated task proportions is zero after averaging for this month's data. Defaulting to equal distribution.")
            if self.task_proportions:
                equal_prop = 1.0 / len(self.task_proportions)
                self.task_proportions = {task: equal_prop for task in self.task_proportions}
            else:
                self.task_proportions = {} # No tasks at all
            return

        self.task_proportions = {task: prop / total_sum for task, prop in self.task_proportions.items()}
        print("Task proportions calculated for the specific month successfully.")

    def forecast(self, expected_orders, forecast_date_str=None):
        if forecast_date_str:
            forecast_date = datetime.strptime(forecast_date_str, '%Y-%m-%d').date()
        else:
            last_historical_date = pd.to_datetime(self.original_historical_df['Supersale_Date']).max().date()
            forecast_date = last_historical_date + timedelta(days=121) 
        
        forecast_date_ordinal = forecast_date.toordinal()
        forecast_month = forecast_date.month

        # --- Filter historical data for the specific month ---
        month_specific_historical_df = self.original_historical_df[self.original_historical_df['Month'] == forecast_month].copy()
        
        if month_specific_historical_df.empty:
            print(f"No historical data available for month {forecast_month}. Cannot train a month-specific model. Falling back to overall average.")
            # Fallback to a simple average from ALL historical data if no month-specific data
            if self.original_historical_df['Total_Orders_Processed'].sum() > 0:
                avg_labor_per_order = self.original_historical_df['Total_Labor_Hours_Actual'].sum() / self.original_historical_df['Total_Orders_Processed'].sum()
            else:
                avg_labor_per_order = 0.06 # Default if no data at all
            forecasted_total_labor_hours = expected_orders * avg_labor_per_order
            self.task_proportions = {} # Clear task proportions if falling back
            self.mean_abs_error_historical = 0 # No MAE if no model
            
        else:
            # Prepare and train the model using only month-specific data
            prepared_month_data = self._prepare_data_for_training(month_specific_historical_df)
            self._train_model(prepared_month_data) # This sets self.model and self.mean_abs_error_historical
            self._calculate_task_proportions(prepared_month_data) # This sets self.task_proportions

            if self.model is None:
                print(f"Model could not be trained for month {forecast_month} (e.g., due to insufficient data for that month). Falling back to month-specific average.")
                # Fallback to simple average from month-specific data if model training failed for that month
                if prepared_month_data['Total_Orders_Processed'].sum() > 0:
                    avg_labor_per_order = prepared_month_data['Total_Labor_Hours_Actual'].sum() / prepared_month_data['Total_Orders_Processed'].sum()
                else:
                    avg_labor_per_order = 0.06 # Default if month-specific data is empty/bad
                forecasted_total_labor_hours = expected_orders * avg_labor_per_order
            else:
                input_features = pd.DataFrame([[expected_orders, forecast_date_ordinal]], 
                                              columns=self.feature_cols)
                forecasted_total_labor_hours = self.model.predict(input_features)[0]
        
        forecasted_total_labor_hours = max(0.0, forecasted_total_labor_hours)

        forecasted_total_workers = int(np.ceil(forecasted_total_labor_hours / 8))

        task_allocations = []
        if not self.task_proportions:
            print("No task proportions available for detailed allocation.")
        else:
            for task, prop in self.task_proportions.items():
                task_labor_hours = forecasted_total_labor_hours * prop
                task_workers = int(np.ceil(task_labor_hours / 8))
                task_allocations.append({
                    'task_name': task.replace('_', ' '),
                    'labor_hours': round(task_labor_hours, 2),
                    'workers': task_workers
                })
            task_allocations.sort(key=lambda x: x['workers'], reverse=True)

        # Confidence interval calculation remains the same
        # Note: If model failed to train, mean_abs_error_historical will be 0, making interval tight.
        lower_bound_labor_hours = max(0.0, forecasted_total_labor_hours - 1.5 * self.mean_abs_error_historical)
        upper_bound_labor_hours = forecasted_total_labor_hours + 1.5 * self.mean_abs_error_historical
        lower_bound_workers = int(np.floor(lower_bound_labor_hours / 8))
        upper_bound_workers = int(np.ceil(upper_bound_labor_hours / 8))

        assumptions = [
            f"The forecast uses historical data ONLY from {datetime(2000, forecast_month, 1).strftime('%B')} events.",
            "Future efficiency trends for this specific month will continue as observed historically.",
            "The relationship between orders and labor hours for this month remains linear with time-based adjustments.",
            "Task-specific labor hour proportions for this month remain consistent with historical averages for this month.",
            "No major external disruptions (e.g., severe weather, new regulations, significant process changes) will occur."
        ]
        
        if self.model is None:
            assumptions.insert(0, "Warning: Insufficient month-specific historical data to train a robust model. Forecast uses a simple average from available historical data for this month (or overall average if no month-specific data).")

        return {
            'forecast_date': forecast_date.strftime('%Y-%m-%d'),
            'expected_orders': expected_orders,
            'forecasted_total_labor_hours': round(forecasted_total_labor_hours, 2),
            'forecasted_total_workers': forecasted_total_workers,
            'confidence_interval_workers': (lower_bound_workers, upper_bound_workers),
            'task_allocations': task_allocations,
            'assumptions': assumptions
        }

# --- LLM Integration Function ---
def get_llm_summary(forecast_data):
    task_breakdown_str = ""
    for task_alloc in forecast_data['task_allocations']:
        task_breakdown_str += f"  - {task_alloc['task_name']}: {task_alloc['workers']:,} workers ({task_alloc['labor_hours']:,} labor hours)\n"

    assumptions_str = ""
    for assumption in forecast_data['assumptions']:
        assumptions_str += f"  • {assumption}\n"

    llm_prompt = f"""
    As an expert logistics and operations manager for Rakuten, please provide a concise, actionable summary of the following Supersale workforce forecast. Highlight key numbers and implications for resource allocation.

    **Forecast Details:**
    - **Supersale Date:** {forecast_data['forecast_date']}
    - **Expected Orders:** {forecast_data['expected_orders']:,}
    - **Total Workers Required:** {forecast_data['forecasted_total_workers']:,} (with a 90% confidence interval of {forecast_data['confidence_interval_workers'][0]:,} to {forecast_data['confidence_interval_workers'][1]:,} workers)
    - **Total Labor Hours:** {forecast_data['forecasted_total_labor_hours']:,} hours

    **Task-Specific Allocation:**
{task_breakdown_str.strip()}

    **Key Assumptions:**
{assumptions_str.strip()}

    **Please structure your summary as follows:**
    1.  **Overall Manpower Need:** State the total worker requirement and confidence range.
    2.  **Key Allocation Highlights:** Mention the top 2-3 tasks requiring the most workers.
    3.  **Operational Implications:** Briefly discuss what these numbers mean for planning.
    4.  **Important Considerations:** Reiterate the most critical assumptions.
    """

    try:
        # Use the 'client' object initialized globally
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Use a model available on your Rakuten endpoint
            messages=[
                {"role": "system", "content": "You are an expert logistics and operations manager, providing concise and actionable summaries. Maintain a professional tone."},
                {"role": "user", "content": llm_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Error generating LLM summary: API Error: {e.args[0]}"
    except Exception as e:
        print(f"An unexpected error occurred during LLM call: {e}")
        return f"Error generating LLM summary: {str(e)}"

# --- Initialize Forecaster (on app startup) ---
historical_data = load_or_generate_historical_data() 
forecaster = WorkforceForecaster(historical_data)

# --- Flask Routes ---
@app.route('/')
def index():
    """Serves the main HTML page for the frontend."""
    return render_template('index.html')

@app.route('/forecast', methods=['POST'])
def forecast_workers():
    """API endpoint to receive forecast requests and return results."""
    data = request.json
    try:
        expected_orders = int(data.get('expectedOrders'))
        forecast_date = data.get('forecastDate') # Can be None if user doesn't specify

        if expected_orders <= 0:
            return jsonify({"error": "Expected orders must be a positive number."}), 400

        # Perform the forecast
        forecast_result = forecaster.forecast(expected_orders, forecast_date)
        # Generate LLM summary and add it to the forecast result
        llm_summary = get_llm_summary(forecast_result)
        forecast_result['llm_summary'] = llm_summary

        return jsonify(forecast_result)

    except ValueError as e:
        # Handle cases where input is not a valid integer
        return jsonify({"error": f"Invalid input for expected orders: {e}"}), 400
    except Exception as e:
        # Catch any other unexpected errors during processing
        print(f"Server error during forecasting: {e}")
        return jsonify({"error": "An unexpected server error occurred during forecasting."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
