"""
Property Feature Engineering and Data Preprocessing Utilities
This module provides utilities for preprocessing property data and extracting features
for house price prediction.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class PropertyFeatureEngineer:
    """
    A comprehensive property feature engineering class
    """
    
    def __init__(self):
        """Initialize the property feature engineer"""
        self.current_year = 2024
    
    def calculate_property_age(self, construction_year):
        """Calculate property age in years"""
        if pd.isna(construction_year):
            return np.nan
        return self.current_year - int(construction_year)
    
    def calculate_renovation_status(self, renovation_year):
        """Calculate years since last renovation"""
        if pd.isna(renovation_year):
            return np.nan
        return self.current_year - int(renovation_year)
    
    def calculate_price_per_sqft(self, price, area_sqft):
        """Calculate price per square foot"""
        if pd.isna(price) or pd.isna(area_sqft) or area_sqft == 0:
            return np.nan
        return price / area_sqft
    
    def calculate_room_ratio(self, bedrooms, bathrooms):
        """Calculate bedroom to bathroom ratio"""
        if pd.isna(bedrooms) or pd.isna(bathrooms) or bathrooms == 0:
            return np.nan
        return bedrooms / bathrooms
    
    def calculate_amenity_score(self, pool, basement, garage_spaces, parking_spots):
        """Calculate overall amenity score"""
        score = 0
        if pool == 1:
            score += 2
        if basement == 1:
            score += 1.5
        score += garage_spaces * 0.5
        score += parking_spots * 0.3
        return score
    
    def calculate_location_score(self, distance_to_city, school_rating, crime_rate, median_income):
        """Calculate overall location desirability score"""
        # Normalize components
        distance_score = max(0, 10 - (distance_to_city / 5))  # Closer is better
        school_score = school_rating  # Already 1-10
        crime_score = max(0, 10 - (crime_rate * 0.5))  # Lower crime is better
        income_score = min(10, median_income / 15000)  # Higher income is better
        
        # Weighted average
        location_score = (distance_score * 0.25 + 
                         school_score * 0.35 + 
                         crime_score * 0.25 + 
                         income_score * 0.15)
        
        return location_score
    
    def calculate_condition_score(self, age_years, hvac_age, roof_age, foundation_quality):
        """Calculate overall property condition score"""
        # Age depreciation (max 10 points)
        age_score = max(0, 10 - (age_years / 10))
        
        # HVAC condition (max 10 points)
        hvac_score = max(0, 10 - (hvac_age / 3))
        
        # Roof condition (max 10 points)
        roof_score = max(0, 10 - (roof_age / 4))
        
        # Foundation quality (already 1-5, scale to 10)
        foundation_score = foundation_quality * 2
        
        # Weighted average
        condition_score = (age_score * 0.25 + 
                          hvac_score * 0.25 + 
                          roof_score * 0.25 + 
                          foundation_score * 0.25)
        
        return condition_score
    
    def calculate_lot_value_ratio(self, lot_size_sqft, area_sqft):
        """Calculate lot size to building area ratio"""
        if pd.isna(lot_size_sqft) or pd.isna(area_sqft) or area_sqft == 0:
            return np.nan
        return lot_size_sqft / area_sqft
    
    def categorize_price_range(self, price):
        """Categorize property into price range"""
        if price < 200000:
            return 'Budget'
        elif price < 400000:
            return 'Mid-Range'
        elif price < 700000:
            return 'Premium'
        else:
            return 'Luxury'
    
    def categorize_property_size(self, area_sqft):
        """Categorize property by size"""
        if area_sqft < 1500:
            return 'Small'
        elif area_sqft < 2500:
            return 'Medium'
        elif area_sqft < 3500:
            return 'Large'
        else:
            return 'Mansion'
    
    def engineer_features(self, property_dict):
        """
        Comprehensive property feature engineering
        """
        features = {}
        
        # Basic features
        features['area_sqft'] = property_dict.get('area_sqft', np.nan)
        features['bedrooms'] = property_dict.get('bedrooms', np.nan)
        features['bathrooms'] = property_dict.get('bathrooms', np.nan)
        
        # Age-related features
        age_years = self.calculate_property_age(property_dict.get('construction_year'))
        features['age_years'] = age_years
        features['is_new_construction'] = int(age_years < 5) if not pd.isna(age_years) else 0
        features['is_historic'] = int(age_years > 50) if not pd.isna(age_years) else 0
        
        # Renovation features
        renovation_years = self.calculate_renovation_status(property_dict.get('renovation_year'))
        features['years_since_renovation'] = renovation_years
        features['recently_renovated'] = int(renovation_years < 5) if not pd.isna(renovation_years) else 0
        
        # Amenity features
        features['pool'] = property_dict.get('pool', 0)
        features['basement'] = property_dict.get('basement', 0)
        features['garage_spaces'] = property_dict.get('garage_spaces', 0)
        features['parking_spots'] = property_dict.get('parking_spots', 0)
        
        amenity_score = self.calculate_amenity_score(
            features['pool'], features['basement'], 
            features['garage_spaces'], features['parking_spots']
        )
        features['amenity_score'] = amenity_score
        
        # Location features
        features['distance_to_city_miles'] = property_dict.get('distance_to_city_miles', np.nan)
        features['school_rating'] = property_dict.get('school_rating', np.nan)
        features['crime_rate'] = property_dict.get('crime_rate_per_1000', np.nan)
        features['median_income_area'] = property_dict.get('median_income_area', np.nan)
        features['population_density'] = property_dict.get('population_density', np.nan)
        
        location_score = self.calculate_location_score(
            features['distance_to_city_miles'],
            features['school_rating'],
            features['crime_rate'],
            features['median_income_area']
        )
        features['location_score'] = location_score
        
        # Condition features
        features['foundation_quality'] = property_dict.get('foundation_quality', np.nan)
        features['hvac_age_years'] = property_dict.get('hvac_age_years', np.nan)
        features['roof_age_years'] = property_dict.get('roof_age_years', np.nan)
        
        condition_score = self.calculate_condition_score(
            features['age_years'],
            features['hvac_age_years'],
            features['roof_age_years'],
            features['foundation_quality']
        )
        features['condition_score'] = condition_score
        
        # Derived features
        features['price_per_sqft'] = self.calculate_price_per_sqft(
            property_dict.get('price'), features['area_sqft']
        )
        
        features['room_ratio'] = self.calculate_room_ratio(
            features['bedrooms'], features['bathrooms']
        )
        
        features['lot_size_sqft'] = property_dict.get('lot_size_sqft', np.nan)
        features['lot_value_ratio'] = self.calculate_lot_value_ratio(
            features['lot_size_sqft'], features['area_sqft']
        )
        
        # Categorical features
        if 'price' in property_dict:
            features['price_category'] = self.categorize_price_range(property_dict['price'])
        
        features['size_category'] = self.categorize_property_size(features['area_sqft'])
        
        return features


def generate_sample_properties(n_properties=500, price_range='all'):
    """
    Generate sample property dataset for demonstration
    """
    engineer = PropertyFeatureEngineer()
    properties = []
    
    np.random.seed(42)
    
    for i in range(n_properties):
        # Generate base property features
        area_sqft = np.random.uniform(800, 5000)
        bedrooms = np.random.randint(1, 6)
        bathrooms = np.random.uniform(1, 4)
        construction_year = np.random.randint(1950, 2024)
        renovation_year = np.random.randint(construction_year, 2024)
        
        # Location features
        distance_to_city = np.random.uniform(0.5, 50)
        school_rating = np.random.uniform(1, 10)
        crime_rate = np.random.uniform(0.5, 15)
        median_income = np.random.uniform(30000, 150000)
        
        # Amenities
        pool = np.random.binomial(1, 0.3)
        basement = np.random.binomial(1, 0.4)
        garage_spaces = np.random.randint(0, 4)
        parking_spots = np.random.randint(0, 5)
        
        # Condition
        foundation_quality = np.random.randint(1, 5)
        hvac_age = np.random.uniform(0, 30)
        roof_age = np.random.uniform(0, 40)
        lot_size = np.random.uniform(2000, 20000)
        
        # Calculate price (simplified)
        base_price = 100000
        area_factor = area_sqft * 150
        room_factor = bedrooms * 50000 + bathrooms * 30000
        age_factor = -(2024 - construction_year) * 500
        location_factor = (-distance_to_city * 2000 + school_rating * 15000 - 
                          crime_rate * 5000 + median_income * 0.3)
        amenities_factor = pool * 40000 + basement * 25000 + garage_spaces * 15000
        condition_factor = (-(2024 - renovation_year) * 1000 + foundation_quality * 20000 - 
                           hvac_age * 1000 - roof_age * 800)
        
        price = base_price + area_factor + room_factor + age_factor + location_factor + amenities_factor + condition_factor
        price = max(50000, price + np.random.normal(0, 50000))
        
        property_dict = {
            'property_id': i + 1,
            'area_sqft': area_sqft,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'construction_year': construction_year,
            'renovation_year': renovation_year,
            'distance_to_city_miles': distance_to_city,
            'school_rating': school_rating,
            'crime_rate_per_1000': crime_rate,
            'median_income_area': median_income,
            'population_density': np.random.uniform(100, 5000),
            'pool': pool,
            'basement': basement,
            'garage_spaces': garage_spaces,
            'parking_spots': parking_spots,
            'foundation_quality': foundation_quality,
            'hvac_age_years': hvac_age,
            'roof_age_years': roof_age,
            'lot_size_sqft': lot_size,
            'price': price
        }
        
        # Engineer features
        features = engineer.engineer_features(property_dict)
        property_dict.update(features)
        
        properties.append(property_dict)
    
    return pd.DataFrame(properties)


def save_sample_dataset(filename='sample_properties.csv', n_properties=500):
    """
    Generate and save sample property dataset
    """
    df = generate_sample_properties(n_properties=n_properties)
    df.to_csv(filename, index=False)
    print(f"✓ Sample property dataset saved to {filename}")
    print(f"  Total properties: {len(df)}")
    print(f"  Average price: ${df['price'].mean():,.2f}")
    print(f"  Price range: ${df['price'].min():,.2f} - ${df['price'].max():,.2f}")
    return df


if __name__ == '__main__':
    # Generate and save sample dataset
    print("Generating sample property dataset...")
    df = save_sample_dataset('/home/ubuntu/sample_properties.csv', n_properties=500)
    
    print("\nDataset Preview:")
    print(df.head())
    
    print("\nDataset Statistics:")
    print(df.describe())
    
    print("\nPrice Category Distribution:")
    print(df['price_category'].value_counts())
    
    print("\nSize Category Distribution:")
    print(df['size_category'].value_counts())
