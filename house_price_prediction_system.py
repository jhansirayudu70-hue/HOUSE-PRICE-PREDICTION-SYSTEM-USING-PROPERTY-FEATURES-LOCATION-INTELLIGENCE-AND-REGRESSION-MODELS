"""
House Price Prediction System Using Property Features, Location Intelligence, and Regression Models
This system predicts residential property prices using machine learning regression algorithms.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import (mean_squared_error, mean_absolute_error, 
                             r2_score, mean_absolute_percentage_error)
import warnings
warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# 1. GENERATE SYNTHETIC HOUSE PRICE DATASET
# ============================================================================

def generate_house_dataset(n_properties=1000, random_state=42):
    """
    Generate a comprehensive house price dataset with multiple property features
    """
    np.random.seed(random_state)
    
    # Property features
    data = {
        'Property_ID': range(1, n_properties + 1),
        'Area_SqFt': np.random.uniform(800, 5000, n_properties),
        'Bedrooms': np.random.randint(1, 6, n_properties),
        'Bathrooms': np.random.uniform(1, 4, n_properties),
        'Age_Years': np.random.uniform(0, 100, n_properties),
        'Garage_Spaces': np.random.randint(0, 4, n_properties),
        'Pool': np.random.binomial(1, 0.3, n_properties),
        'Basement': np.random.binomial(1, 0.4, n_properties),
        'Parking_Spots': np.random.randint(0, 5, n_properties),
        'Distance_to_City_Miles': np.random.uniform(0.5, 50, n_properties),
        'School_Rating': np.random.uniform(1, 10, n_properties),
        'Crime_Rate_Per_1000': np.random.uniform(0.5, 15, n_properties),
        'Median_Income_Area': np.random.uniform(30000, 150000, n_properties),
        'Population_Density': np.random.uniform(100, 5000, n_properties),
        'Renovation_Year': np.random.uniform(1950, 2024, n_properties),
        'Lot_Size_SqFt': np.random.uniform(2000, 20000, n_properties),
        'Foundation_Quality': np.random.randint(1, 5, n_properties),
        'HVAC_Age_Years': np.random.uniform(0, 30, n_properties),
        'Roof_Age_Years': np.random.uniform(0, 40, n_properties),
    }
    
    df = pd.DataFrame(data)
    
    # Create target variable: House Price
    # Price is influenced by multiple factors
    base_price = 100000
    
    # Area contribution (primary factor)
    area_factor = df['Area_SqFt'] * 150
    
    # Bedroom/Bathroom contribution
    room_factor = (df['Bedrooms'] * 50000 + df['Bathrooms'] * 30000)
    
    # Age depreciation
    age_factor = -df['Age_Years'] * 500
    
    # Location factors
    location_factor = (
        -df['Distance_to_City_Miles'] * 2000 +
        df['School_Rating'] * 15000 -
        df['Crime_Rate_Per_1000'] * 5000 +
        df['Median_Income_Area'] * 0.3
    )
    
    # Amenities
    amenities_factor = (
        df['Pool'] * 40000 +
        df['Basement'] * 25000 +
        df['Garage_Spaces'] * 15000
    )
    
    # Condition factors
    condition_factor = (
        (2024 - df['Renovation_Year']) * (-1000) +
        df['Foundation_Quality'] * 20000 -
        df['HVAC_Age_Years'] * 1000 -
        df['Roof_Age_Years'] * 800
    )
    
    # Add randomness
    noise = np.random.normal(0, 50000, n_properties)
    
    df['Price'] = (base_price + area_factor + room_factor + age_factor + 
                   location_factor + amenities_factor + condition_factor + noise)
    
    # Ensure positive prices
    df['Price'] = df['Price'].clip(lower=50000)
    
    return df

# ============================================================================
# 2. DATA EXPLORATION AND ANALYSIS
# ============================================================================

def explore_house_data(df):
    """
    Perform exploratory data analysis on house dataset
    """
    print("=" * 80)
    print("HOUSE PRICE DATASET OVERVIEW")
    print("=" * 80)
    print(f"\nDataset Shape: {df.shape}")
    print(f"Number of Properties: {df.shape[0]}")
    print(f"Number of Features: {df.shape[1]}")
    
    print("\n" + "=" * 80)
    print("PRICE STATISTICS")
    print("=" * 80)
    print(f"Mean Price: ${df['Price'].mean():,.2f}")
    print(f"Median Price: ${df['Price'].median():,.2f}")
    print(f"Min Price: ${df['Price'].min():,.2f}")
    print(f"Max Price: ${df['Price'].max():,.2f}")
    print(f"Std Dev: ${df['Price'].std():,.2f}")
    
    print("\n" + "=" * 80)
    print("PROPERTY FEATURES SUMMARY")
    print("=" * 80)
    print(df.describe())
    
    print("\n" + "=" * 80)
    print("MISSING VALUES")
    print("=" * 80)
    print(df.isnull().sum())
    
    return df

# ============================================================================
# 3. VISUALIZATION FUNCTIONS
# ============================================================================

def create_price_distribution_plot(df):
    """
    Create visualization of house price distribution
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Histogram
    ax1.hist(df['Price'], bins=50, color='steelblue', alpha=0.8, edgecolor='black')
    ax1.set_title('Distribution of House Prices', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Price ($)')
    ax1.set_ylabel('Frequency')
    ax1.grid(axis='y', alpha=0.3)
    
    # Box plot
    ax2.boxplot(df['Price'], vert=True)
    ax2.set_title('House Price Box Plot', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Price ($)')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.suptitle('House Price Distribution Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/price_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Price distribution plot saved")
    plt.close()

def create_feature_correlation_plot(df):
    """
    Create correlation heatmap for house features
    """
    plt.figure(figsize=(14, 10))
    
    # Select numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    correlation_matrix = numeric_df.corr()
    
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    
    plt.title('Correlation Matrix: Property Features and Price', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_correlation.png', dpi=300, bbox_inches='tight')
    print("✓ Feature correlation plot saved")
    plt.close()

def create_feature_price_relationships(df):
    """
    Create scatter plots showing relationship between key features and price
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Property Features vs House Price', fontsize=14, fontweight='bold')
    
    features = ['Area_SqFt', 'Bedrooms', 'Age_Years', 
                'Distance_to_City_Miles', 'School_Rating', 'Crime_Rate_Per_1000']
    
    for idx, feature in enumerate(features):
        ax = axes[idx // 3, idx % 3]
        ax.scatter(df[feature], df['Price'], alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel(feature)
        ax.set_ylabel('Price ($)')
        ax.set_title(f'{feature} vs Price', fontweight='bold')
        ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_price_relationships.png', dpi=300, bbox_inches='tight')
    print("✓ Feature-price relationships plot saved")
    plt.close()

def create_model_comparison_plot(results):
    """
    Create bar chart comparing model performance metrics
    """
    models = list(results.keys())
    r2_scores = [results[model]['R2'] for model in models]
    rmse = [results[model]['RMSE'] for model in models]
    mae = [results[model]['MAE'] for model in models]
    
    x = np.arange(len(models))
    width = 0.25
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # R² Score comparison
    ax1.bar(x, r2_scores, width, label='R² Score', alpha=0.8, edgecolor='black')
    ax1.set_title('Model R² Score Comparison', fontweight='bold', fontsize=12)
    ax1.set_ylabel('R² Score')
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=45, ha='right')
    ax1.set_ylim([0, 1.1])
    ax1.grid(axis='y', alpha=0.3)
    
    # Error metrics comparison
    x_pos = np.arange(len(models))
    width = 0.35
    ax2.bar(x_pos - width/2, rmse, width, label='RMSE', alpha=0.8, edgecolor='black')
    ax2.bar(x_pos + width/2, mae, width, label='MAE', alpha=0.8, edgecolor='black')
    ax2.set_title('Model Error Metrics Comparison', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Error ($)')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(models, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/model_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Model comparison plot saved")
    plt.close()

def create_residuals_plot(y_test, y_pred, model_name):
    """
    Create residuals visualization
    """
    residuals = y_test - y_pred
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Residuals scatter plot
    ax1.scatter(y_pred, residuals, alpha=0.6, edgecolors='black', linewidth=0.5)
    ax1.axhline(y=0, color='r', linestyle='--', linewidth=2)
    ax1.set_xlabel('Predicted Price ($)')
    ax1.set_ylabel('Residuals ($)')
    ax1.set_title(f'Residual Plot - {model_name}', fontweight='bold')
    ax1.grid(alpha=0.3)
    
    # Residuals histogram
    ax2.hist(residuals, bins=30, color='steelblue', alpha=0.8, edgecolor='black')
    ax2.set_xlabel('Residuals ($)')
    ax2.set_ylabel('Frequency')
    ax2.set_title(f'Residual Distribution - {model_name}', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'/home/ubuntu/residuals_{model_name.lower().replace(" ", "_")}.png', 
                dpi=300, bbox_inches='tight')
    print(f"✓ Residuals plot for {model_name} saved")
    plt.close()

def create_prediction_accuracy_plot(y_test, y_pred, model_name):
    """
    Create actual vs predicted price plot
    """
    plt.figure(figsize=(10, 8))
    
    plt.scatter(y_test, y_pred, alpha=0.6, edgecolors='black', linewidth=0.5, s=50)
    
    # Perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    plt.xlabel('Actual Price ($)', fontsize=12)
    plt.ylabel('Predicted Price ($)', fontsize=12)
    plt.title(f'Actual vs Predicted Prices - {model_name}', fontweight='bold', fontsize=14)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'/home/ubuntu/prediction_accuracy_{model_name.lower().replace(" ", "_")}.png', 
                dpi=300, bbox_inches='tight')
    print(f"✓ Prediction accuracy plot for {model_name} saved")
    plt.close()

def create_feature_importance_plot(feature_importance, feature_names):
    """
    Create feature importance visualization
    """
    plt.figure(figsize=(12, 8))
    
    indices = np.argsort(feature_importance)[::-1][:15]  # Top 15 features
    
    plt.bar(range(len(indices)), feature_importance[indices], 
            color='steelblue', alpha=0.8, edgecolor='black')
    plt.xticks(range(len(indices)), 
               [feature_names[i] for i in indices], rotation=45, ha='right')
    
    plt.title('Top 15 Important Features for Price Prediction', fontweight='bold', fontsize=14)
    plt.ylabel('Importance Score')
    plt.xlabel('Features')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('/home/ubuntu/feature_importance.png', dpi=300, bbox_inches='tight')
    print("✓ Feature importance plot saved")
    plt.close()

def create_price_by_location_plot(df):
    """
    Create visualization of price by location
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Price vs Distance to City
    ax1.scatter(df['Distance_to_City_Miles'], df['Price'], alpha=0.6, edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('Distance to City (Miles)')
    ax1.set_ylabel('Price ($)')
    ax1.set_title('House Price vs Distance to City', fontweight='bold')
    ax1.grid(alpha=0.3)
    
    # Price vs School Rating
    ax2.scatter(df['School_Rating'], df['Price'], alpha=0.6, edgecolors='black', linewidth=0.5, color='green')
    ax2.set_xlabel('School Rating')
    ax2.set_ylabel('Price ($)')
    ax2.set_title('House Price vs School Rating', fontweight='bold')
    ax2.grid(alpha=0.3)
    
    plt.suptitle('Location Intelligence: Impact on House Prices', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/ubuntu/location_intelligence.png', dpi=300, bbox_inches='tight')
    print("✓ Location intelligence plot saved")
    plt.close()

# ============================================================================
# 4. MACHINE LEARNING MODEL TRAINING AND EVALUATION
# ============================================================================

def train_and_evaluate_models(X_train, X_test, y_train, y_test, feature_names):
    """
    Train multiple machine learning regression models and evaluate their performance
    """
    results = {}
    
    print("\n" + "=" * 80)
    print("MACHINE LEARNING MODEL TRAINING AND EVALUATION")
    print("=" * 80)
    
    # 1. Linear Regression
    print("\n[1/5] Training Linear Regression Model...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    y_pred_lr = lr_model.predict(X_test)
    
    results['Linear Regression'] = {
        'Model': lr_model,
        'Predictions': y_pred_lr,
        'R2': r2_score(y_test, y_pred_lr),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_lr)),
        'MAE': mean_absolute_error(y_test, y_pred_lr),
        'MAPE': mean_absolute_percentage_error(y_test, y_pred_lr)
    }
    
    print(f"   R² Score: {results['Linear Regression']['R2']:.4f}")
    print(f"   RMSE: ${results['Linear Regression']['RMSE']:,.2f}")
    print(f"   MAE: ${results['Linear Regression']['MAE']:,.2f}")
    
    # 2. Ridge Regression
    print("\n[2/5] Training Ridge Regression Model...")
    ridge_model = Ridge(alpha=1.0)
    ridge_model.fit(X_train, y_train)
    y_pred_ridge = ridge_model.predict(X_test)
    
    results['Ridge Regression'] = {
        'Model': ridge_model,
        'Predictions': y_pred_ridge,
        'R2': r2_score(y_test, y_pred_ridge),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_ridge)),
        'MAE': mean_absolute_error(y_test, y_pred_ridge),
        'MAPE': mean_absolute_percentage_error(y_test, y_pred_ridge)
    }
    
    print(f"   R² Score: {results['Ridge Regression']['R2']:.4f}")
    print(f"   RMSE: ${results['Ridge Regression']['RMSE']:,.2f}")
    print(f"   MAE: ${results['Ridge Regression']['MAE']:,.2f}")
    
    # 3. Lasso Regression
    print("\n[3/5] Training Lasso Regression Model...")
    lasso_model = Lasso(alpha=1.0)
    lasso_model.fit(X_train, y_train)
    y_pred_lasso = lasso_model.predict(X_test)
    
    results['Lasso Regression'] = {
        'Model': lasso_model,
        'Predictions': y_pred_lasso,
        'R2': r2_score(y_test, y_pred_lasso),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_lasso)),
        'MAE': mean_absolute_error(y_test, y_pred_lasso),
        'MAPE': mean_absolute_percentage_error(y_test, y_pred_lasso)
    }
    
    print(f"   R² Score: {results['Lasso Regression']['R2']:.4f}")
    print(f"   RMSE: ${results['Lasso Regression']['RMSE']:,.2f}")
    print(f"   MAE: ${results['Lasso Regression']['MAE']:,.2f}")
    
    # 4. Random Forest Regressor
    print("\n[4/5] Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)
    
    results['Random Forest'] = {
        'Model': rf_model,
        'Predictions': y_pred_rf,
        'R2': r2_score(y_test, y_pred_rf),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_rf)),
        'MAE': mean_absolute_error(y_test, y_pred_rf),
        'MAPE': mean_absolute_percentage_error(y_test, y_pred_rf),
        'Feature_Importance': rf_model.feature_importances_
    }
    
    print(f"   R² Score: {results['Random Forest']['R2']:.4f}")
    print(f"   RMSE: ${results['Random Forest']['RMSE']:,.2f}")
    print(f"   MAE: ${results['Random Forest']['MAE']:,.2f}")
    
    # 5. Gradient Boosting Regressor
    print("\n[5/5] Training Gradient Boosting Regressor...")
    gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    gb_model.fit(X_train, y_train)
    y_pred_gb = gb_model.predict(X_test)
    
    results['Gradient Boosting'] = {
        'Model': gb_model,
        'Predictions': y_pred_gb,
        'R2': r2_score(y_test, y_pred_gb),
        'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_gb)),
        'MAE': mean_absolute_error(y_test, y_pred_gb),
        'MAPE': mean_absolute_percentage_error(y_test, y_pred_gb),
        'Feature_Importance': gb_model.feature_importances_
    }
    
    print(f"   R² Score: {results['Gradient Boosting']['R2']:.4f}")
    print(f"   RMSE: ${results['Gradient Boosting']['RMSE']:,.2f}")
    print(f"   MAE: ${results['Gradient Boosting']['MAE']:,.2f}")
    
    print("\n" + "=" * 80)
    print("MODEL PERFORMANCE SUMMARY")
    print("=" * 80)
    
    summary_df = pd.DataFrame({
        'Model': list(results.keys()),
        'R² Score': [results[m]['R2'] for m in results.keys()],
        'RMSE ($)': [results[m]['RMSE'] for m in results.keys()],
        'MAE ($)': [results[m]['MAE'] for m in results.keys()],
        'MAPE (%)': [results[m]['MAPE'] * 100 for m in results.keys()]
    })
    
    print(summary_df.to_string(index=False))
    
    # Identify best model
    best_model_name = max(results.keys(), key=lambda x: results[x]['R2'])
    print(f"\n✓ Best Performing Model: {best_model_name}")
    print(f"  R² Score: {results[best_model_name]['R2']:.4f}")
    print(f"  RMSE: ${results[best_model_name]['RMSE']:,.2f}")
    
    return results, best_model_name

# ============================================================================
# 5. MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function
    """
    print("\n" + "=" * 80)
    print("HOUSE PRICE PREDICTION SYSTEM")
    print("=" * 80)
    
    # Generate dataset
    print("\n[Step 1] Generating House Price Dataset...")
    df = generate_house_dataset(n_properties=1000)
    print(f"✓ Dataset generated with {len(df)} properties and {len(df.columns)} features")
    
    # Explore data
    print("\n[Step 2] Exploring House Dataset...")
    explore_house_data(df)
    
    # Prepare features and target
    print("\n[Step 3] Preparing Data for Model Training...")
    feature_columns = [col for col in df.columns if col not in ['Property_ID', 'Price']]
    
    X = df[feature_columns]
    y = df['Price']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"✓ Training set size: {len(X_train)}")
    print(f"✓ Test set size: {len(X_test)}")
    
    # Train models
    print("\n[Step 4] Training Machine Learning Models...")
    results, best_model_name = train_and_evaluate_models(X_train_scaled, X_test_scaled, 
                                                         y_train, y_test, feature_columns)
    
    # Generate visualizations
    print("\n[Step 5] Generating Visualizations...")
    print("Creating price distribution plot...")
    create_price_distribution_plot(df)
    
    print("Creating feature correlation plot...")
    create_feature_correlation_plot(df)
    
    print("Creating feature-price relationships...")
    create_feature_price_relationships(df)
    
    print("Creating location intelligence plot...")
    create_price_by_location_plot(df)
    
    print("Creating model comparison plot...")
    create_model_comparison_plot(results)
    
    # Create plots for best model
    best_model_results = results[best_model_name]
    print(f"Creating residuals plot for {best_model_name}...")
    create_residuals_plot(y_test, best_model_results['Predictions'], best_model_name)
    
    print(f"Creating prediction accuracy plot for {best_model_name}...")
    create_prediction_accuracy_plot(y_test, best_model_results['Predictions'], best_model_name)
    
    # Feature importance for ensemble models
    if 'Feature_Importance' in best_model_results:
        print(f"Creating feature importance plot for {best_model_name}...")
        create_feature_importance_plot(best_model_results['Feature_Importance'], feature_columns)
    
    print("\n" + "=" * 80)
    print("EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nGenerated Visualizations:")
    print("  1. price_distribution.png")
    print("  2. feature_correlation.png")
    print("  3. feature_price_relationships.png")
    print("  4. location_intelligence.png")
    print("  5. model_comparison.png")
    print("  6. residuals_*.png")
    print("  7. prediction_accuracy_*.png")
    print("  8. feature_importance.png")
    
    return df, results, best_model_name

if __name__ == "__main__":
    df, results, best_model_name = main()
