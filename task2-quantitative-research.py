# Prepare the gas price data
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

df = pd.read_csv("Nat_Gas.csv", parse_dates=['Dates'],
                 date_parser=lambda x: pd.to_datetime(x, format='%m/%d/%y'))
df = df.set_index('Dates')

# Build a pricing function
def price_contract(df,
                   injection_dates, 
                   withdrawal_dates,
                   injection_rate,  # Max volume injected per month (MMBtu)
                   withdrawal_rate, # Max volume withdrawn per month (MMBtu)
                   max_storage,     # Max storage capacity (MMBtu)
                   storage_cost_per_month):  # Storage cost per MMBtu per month (e.g., 0.05 = $0.05/MMBtu/month)
    
    storage_volume = 0
    total_value = 0

    print("=== Injection Period ===")
    for month in sorted(injection_dates):
        price = df.loc[month, 'Prices']

        inject_amount = min(injection_rate, max_storage - storage_volume)
        if inject_amount > 0:
            cost = inject_amount * price
            total_value -= cost
            storage_volume += inject_amount
            print(f"{month.date()}: Injected {inject_amount} MMBtu at ${price:.2f} (Storage: {storage_volume} MMBtu)")
            if storage_volume == max_storage:
                print(f"{month.date()}: ⚠ Storage is full! ({storage_volume} MMBtu)")
        else:
            print(f"{month.date()}: ❌ Cannot inject! Storage already full at {storage_volume} MMBtu")

        # Storage cost after injection
        if storage_volume > 0:
            cost = storage_volume * storage_cost_per_month
            total_value -= cost
            print(f"{month.date()}: Storage cost ${cost:.2f} for {storage_volume} MMBtu")

    print("\n=== Withdrawal Period ===")
    for month in sorted(withdrawal_dates):
        price = df.loc[month, 'Prices']

        withdrawal_amount = min(withdrawal_rate, storage_volume)
        if withdrawal_amount > 0:
            revenue = withdrawal_amount * price
            total_value += revenue
            storage_volume -= withdrawal_amount
            print(f"{month.date()}: Withdrew {withdrawal_amount} MMBtu at ${price:.2f} (Storage: {storage_volume} MMBtu)")
            if withdrawal_amount < withdrawal_rate:
                print(f"{month.date()}: ⚠ Cannot withdraw full amount. Only {withdrawal_amount} MMBtu available.")
        else:
            print(f"{month.date()}: ❌ No gas to withdraw!")

        # Storage cost after withdrawal
        if storage_volume > 0:
            cost = storage_volume * storage_cost_per_month
            total_value -= cost
            print(f"{month.date()}: Storage cost ${cost:.2f} for {storage_volume} MMBtu")

    print(f"\nFinal contract value: ${total_value:.2f}")
    return total_value

# Inputs
injection_dates = pd.to_datetime([
    '2023-04-30', '2023-05-31', '2023-06-30', '2023-07-31',
    '2023-08-31', '2023-09-30'
])

withdrawal_dates = pd.to_datetime([
    '2023-10-31', '2023-11-30', '2023-12-31', '2024-01-31',
    '2024-02-29', '2024-03-31'
])

price_contract(
    df=df,
    injection_dates=injection_dates,
    withdrawal_dates=withdrawal_dates,
    injection_rate=500000,
    withdrawal_rate=500000,
    max_storage=6000000,
    storage_cost_per_month=0.05
)
