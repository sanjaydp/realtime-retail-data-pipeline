# PowerBI Dashboard Setup

This directory contains the PowerBI dashboard configuration and setup for the retail data pipeline visualization.

## Components

- `RetailAnalytics.pbix`: Main PowerBI dashboard file
- `data_model.json`: Data model configuration
- `dashboard_config.json`: Dashboard layout and visualization settings

## Dashboard Features

1. **Sales Analytics**
   - Real-time sales by store location
   - Product category performance
   - Payment method distribution
   - Hourly/daily/weekly trends

2. **Inventory Management**
   - Current stock levels
   - Low stock alerts
   - Reorder recommendations
   - Stock movement trends

3. **Customer Insights**
   - Customer segmentation
   - Purchase patterns
   - Customer lifetime value
   - Geographic distribution

4. **Performance Metrics**
   - Revenue metrics
   - Transaction volume
   - Average order value
   - Conversion rates

## Setup Instructions

1. Install PowerBI Desktop (if not already installed)
2. Open `RetailAnalytics.pbix` in PowerBI Desktop
3. Configure data source connections:
   - PostgreSQL connection for historical data
   - Kafka connection for real-time updates
4. Refresh data model
5. Publish to PowerBI Service (optional)

## Data Refresh Schedule

- Real-time data: Every 5 minutes
- Historical data: Daily at 1:00 AM UTC
- Aggregated metrics: Weekly on Sundays

## Security

- Row-level security implemented for store-level access
- Data encryption in transit and at rest
- Role-based access control

## Troubleshooting

1. **Connection Issues**
   - Verify database credentials
   - Check network connectivity
   - Ensure Kafka topics are accessible

2. **Data Refresh Failures**
   - Check data source availability
   - Verify query performance
   - Review error logs

3. **Visualization Issues**
   - Clear browser cache
   - Update PowerBI Desktop
   - Check data model relationships 