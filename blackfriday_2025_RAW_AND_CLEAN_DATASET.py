#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
import numpy as np
import datetime as dt

rng = np.random.default_rng(42)

# 1) PRODUCTS (2025)
def make_products(n=120):
    categories = [
        ("Electronics", ["Headphones", "Laptop", "Smartwatch", "TV", "Tablet", "Speaker"]),
        ("Apparel", ["T-Shirt", "Jeans", "Jacket", "Shoes", "Dress", "Hoodie"]),
        ("Home", ["Cookware", "Vacuum", "Bedding", "Lamp", "Storage", "Appliance"]),
        ("Beauty", ["Skincare", "Makeup", "Fragrance", "Haircare"]),
        ("Grocery", ["Snacks", "Beverages", "Pantry", "Frozen"]),
    ]
    brands = ["Nova", "Apex", "Zenith", "Orion", "Pulse", "Terra", "Luma", "Vertex"]

    rows = []
    for i in range(1, n + 1):
        cat, subcats = categories[rng.integers(0, len(categories))]
        sub = subcats[rng.integers(0, len(subcats))]
        brand = brands[rng.integers(0, len(brands))]
        product_id = f"P{i:04d}"
        product_name = f"{brand} {sub}"

        # pricing logic
        base = {
            "Electronics": (80, 1200),
            "Apparel": (12, 180),
            "Home": (18, 350),
            "Beauty": (10, 220),
            "Grocery": (2, 40),
        }[cat]
        regular_price = float(round(rng.uniform(base[0], base[1]), 2))
        cost_price = float(round(regular_price * rng.uniform(0.45, 0.72), 2))

        rows.append([product_id, product_name, cat, sub, brand, regular_price, cost_price])

    return pd.DataFrame(rows, columns=[
        "product_id","product_name","category","subcategory","brand","regular_price","cost_price"
    ])

# -----------------------------
# 2) STORES (2025)
# -----------------------------
def make_stores(n=30):
    regions = ["Northeast","Midwest","South","West"]
    states = ["NY","NJ","PA","MA","IL","OH","GA","FL","TX","CA","WA","AZ","NC","VA","MI"]
    cities = ["New York","Boston","Philadelphia","Chicago","Austin","Dallas","Miami","Atlanta","Seattle","Phoenix","San Jose","Tampa","Charlotte","Detroit"]

    rows = []
    for i in range(1, n + 1):
        store_id = f"S{i:03d}"
        region = regions[rng.integers(0, len(regions))]
        state = states[rng.integers(0, len(states))]
        city = cities[rng.integers(0, len(cities))]
        store_type = rng.choice(["Urban","Suburban","Outlet"], p=[0.35,0.5,0.15])
        rows.append([store_id, region, state, city, store_type])

    return pd.DataFrame(rows, columns=["store_id","region","state","city","store_type"])

# -----------------------------
# 3) PROMOTIONS (2025)
# -----------------------------
def make_promotions(n=18):
    promo_types = ["BOGO","Percent Off","Flash Deal","Bundle","Clearance","Loyalty Exclusive"]
    channels = ["Online","In-Store"]
    groups = ["BlackFriday_Main","BlackFriday_Early","CyberWeek","Clearance_Push","Loyalty_Drop"]

    rows = []
    for i in range(1, n + 1):
        promotion_id = f"PR{i:03d}"
        promo_type = promo_types[rng.integers(0, len(promo_types))]
        channel = channels[rng.integers(0, len(channels))]
        promo_group = groups[rng.integers(0, len(groups))]

        # discount distribution
        if promo_type == "BOGO":
            discount_pct = 50
        elif promo_type == "Flash Deal":
            discount_pct = int(rng.integers(20, 60))
        elif promo_type == "Percent Off":
            discount_pct = int(rng.integers(10, 45))
        elif promo_type == "Clearance":
            discount_pct = int(rng.integers(30, 70))
        elif promo_type == "Bundle":
            discount_pct = int(rng.integers(10, 35))
        else:  # Loyalty Exclusive
            discount_pct = int(rng.integers(10, 40))

        # campaign dates around BF week (Nov 22–30, 2025)
        start_day = int(rng.integers(22, 28))
        end_day = int(rng.integers(max(start_day, 25), 31))

        start_date = dt.date(2025, 11, start_day)
        end_date = dt.date(2025, 11, end_day)

        rows.append([promotion_id, promo_type, discount_pct, channel, promo_group, start_date, end_date])

    return pd.DataFrame(rows, columns=[
        "promotion_id","promo_type","discount_pct","channel","promo_group","start_date","end_date"
    ])

# -----------------------------
# 4) ORDERS RAW (2025)  ✅ error-proof datetime
# -----------------------------
def sample_datetime_2025():
    days = pd.date_range("2025-11-22", "2025-11-30", freq="D")

    # Heavier on Black Friday (Nov 28) + weekend
    weights = []
    for d in days:
        d_ts = pd.Timestamp(d)
        if d_ts.date() == dt.date(2025, 11, 28):
            w = 7.5
        elif d_ts.weekday() in (5, 6):
            w = 2.4
        else:
            w = 1.0
        weights.append(w)
    weights = np.array(weights) / np.sum(weights)

    # rng.choice returns numpy.datetime64 -> convert safely
    day = pd.Timestamp(rng.choice(days, p=weights))

    # peak hours
    hours = np.arange(0, 24)
    h_w = np.ones(24)
    h_w[10:15] *= 2.0   # midday peak
    h_w[18:22] *= 1.8   # evening peak
    h_w[0:2]   *= 1.2   # midnight-ish
    h_w = h_w / h_w.sum()

    hour = int(rng.choice(hours, p=h_w))
    minute = int(rng.integers(0, 60))
    second = int(rng.integers(0, 60))

    return dt.datetime(day.year, day.month, day.day, hour, minute, second)

def make_orders(products, stores, promos, n=2000):
    product_ids = products["product_id"].to_numpy()
    store_ids = stores["store_id"].to_numpy()
    promo_ids = promos["promotion_id"].to_numpy()

    rows = []
    for i in range(1, n + 1):
        order_id = f"BF2025-{i:06d}"
        order_dt = sample_datetime_2025()

        store_id = store_ids[rng.integers(0, len(store_ids))]
        product_id = product_ids[rng.integers(0, len(product_ids))]

        # channel
        channel = rng.choice(["Online", "In-Store"], p=[0.58, 0.42])

        # attach promo ~60% of time (BF heavy)
        has_promo = rng.random() < 0.62
        promotion_id = promo_ids[rng.integers(0, len(promo_ids))] if has_promo else np.nan

        # discount logic
        reg_price = float(products.loc[products["product_id"] == product_id, "regular_price"].iloc[0])
        if has_promo:
            disc = float(promos.loc[promos["promotion_id"] == promotion_id, "discount_pct"].iloc[0])
            # small noise
            disc = float(np.clip(disc + rng.normal(0, 2.0), 0, 75))
        else:
            # occasional manual markdown
            disc = 0.0 if rng.random() > 0.12 else float(rng.uniform(5, 18))

        unit_selling_price = reg_price * (1 - disc / 100.0)
        unit_selling_price *= (1 + rng.normal(0, 0.015))
        unit_selling_price = float(round(max(unit_selling_price, 0.5), 2))

        # units
        category = products.loc[products["product_id"] == product_id, "category"].iloc[0]
        lam = 1.2 if channel == "Online" else 1.5
        lam *= 1.0 if str(category).lower() == "electronics" else 1.25
        units = int(np.clip(rng.poisson(lam) + 1, 1, 8))

        payment_method = rng.choice(["Card", "Cash", "Digital Wallet"], p=[0.62, 0.14, 0.24])
        order_status = rng.choice(["Completed", "Returned", "Canceled"], p=[0.93, 0.05, 0.02])

        rows.append([
            order_id,
            order_dt.strftime("%Y-%m-%d %H:%M:%S"),
            store_id,
            product_id,
            promotion_id,
            channel,
            payment_method,
            units,
            unit_selling_price,
            round(disc, 1),
            order_status
        ])

    return pd.DataFrame(rows, columns=[
        "order_id","order_datetime","store_id","product_id","promotion_id",
        "channel","payment_method","units","unit_selling_price","discount_pct_applied","order_status"
    ])

# -----------------------------
# RUN + SAVE (creates 4 CSVs)
# -----------------------------
products_2025 = make_products(n=120)
stores_2025   = make_stores(n=30)
promos_2025   = make_promotions(n=18)
orders_2025   = make_orders(products_2025, stores_2025, promos_2025, n=2000)

products_2025.to_csv("bf_productsdata_2025.csv", index=False)
stores_2025.to_csv("bf_storesdata_2025.csv", index=False)
promos_2025.to_csv("bf_promotionsdata_2025.csv", index=False)
orders_2025.to_csv("bf_orders_rawdata_2025.csv", index=False)

print("DONE ✅ Created 4 files in this folder:")
print("- bf_productsdata_2025.csv")
print("- bf_storesdata_2025.csv")
print("- bf_promotionsdata_2025.csv")
print("- bf_orders_rawdata_2025.csv")
print("\nRows:", {"products": len(products_2025), "stores": len(stores_2025), "promotions": len(promos_2025), "orders": len(orders_2025)})


# In[9]:


import pandas as pd
import numpy as np

# -----------------------------
# LOAD (same folder)
# -----------------------------
products = pd.read_csv("bf_productsdata_2025.csv")
stores   = pd.read_csv("bf_storesdata_2025.csv")
promos   = pd.read_csv("bf_promotionsdata_2025.csv")
orders   = pd.read_csv("bf_orders_rawdata_2025.csv")

quality_log = []

def log(step, before, after, notes=""):
    quality_log.append({
        "step": step,
        "rows_before": before,
        "rows_after": after,
        "rows_removed": before - after,
        "notes": notes
    })

# -----------------------------
# CLEAN: PRODUCTS
# -----------------------------
b = len(products)

# trim text
for c in ["product_id","product_name","category","subcategory","brand"]:
    products[c] = products[c].astype(str).str.strip()

# numeric types
products["regular_price"] = pd.to_numeric(products["regular_price"], errors="coerce")
products["cost_price"]    = pd.to_numeric(products["cost_price"], errors="coerce")

# drop invalid IDs
products = products[products["product_id"].notna() & (products["product_id"] != "")]
products = products.drop_duplicates(subset=["product_id"], keep="first")

# drop invalid prices
products = products[(products["regular_price"] > 0) & (products["cost_price"] > 0)]
products = products[products["cost_price"] <= products["regular_price"]]

log("products_clean", b, len(products), "trim text, enforce numeric prices, drop dup IDs, remove invalid pricing")

# -----------------------------
# CLEAN: STORES
# -----------------------------
b = len(stores)

for c in ["store_id","region","state","city","store_type"]:
    stores[c] = stores[c].astype(str).str.strip()

stores = stores[stores["store_id"].notna() & (stores["store_id"] != "")]
stores = stores.drop_duplicates(subset=["store_id"], keep="first")

log("stores_clean", b, len(stores), "trim text, drop dup IDs")

# -----------------------------
# CLEAN: PROMOTIONS
# -----------------------------
b = len(promos)

for c in ["promotion_id","promo_type","channel","promo_group"]:
    promos[c] = promos[c].astype(str).str.strip()

promos["discount_pct"] = pd.to_numeric(promos["discount_pct"], errors="coerce")
promos["start_date"] = pd.to_datetime(promos["start_date"], errors="coerce").dt.date
promos["end_date"]   = pd.to_datetime(promos["end_date"], errors="coerce").dt.date

promos = promos[promos["promotion_id"].notna() & (promos["promotion_id"] != "")]
promos = promos.drop_duplicates(subset=["promotion_id"], keep="first")

# discount bounds
promos = promos[(promos["discount_pct"] >= 0) & (promos["discount_pct"] <= 80)]

# valid dates
promos = promos[promos["start_date"].notna() & promos["end_date"].notna()]
promos = promos[promos["end_date"] >= promos["start_date"]]

log("promotions_clean", b, len(promos), "trim text, enforce discount bounds, validate dates, drop dup IDs")

# -----------------------------
# CLEAN: ORDERS
# -----------------------------
b = len(orders)

# trim text columns
for c in ["order_id","store_id","product_id","promotion_id","channel","payment_method","order_status"]:
    orders[c] = orders[c].astype(str).str.strip()
    orders[c] = orders[c].replace({"nan": np.nan, "None": np.nan})

# datetime
orders["order_datetime"] = pd.to_datetime(orders["order_datetime"], errors="coerce")

# numeric
orders["units"] = pd.to_numeric(orders["units"], errors="coerce")
orders["unit_selling_price"] = pd.to_numeric(orders["unit_selling_price"], errors="coerce")
orders["discount_pct_applied"] = pd.to_numeric(orders["discount_pct_applied"], errors="coerce")

# drop invalid core fields
orders = orders[orders["order_datetime"].notna()]
orders = orders[orders["order_id"].notna() & (orders["order_id"] != "")]
orders = orders[orders["store_id"].notna() & (orders["store_id"] != "")]
orders = orders[orders["product_id"].notna() & (orders["product_id"] != "")]

# fix units
orders["units"] = orders["units"].fillna(1).clip(1, 8).astype(int)

# fix price/discount
orders["unit_selling_price"] = orders["unit_selling_price"].where(orders["unit_selling_price"] > 0)
orders = orders[orders["unit_selling_price"].notna()]

orders["discount_pct_applied"] = orders["discount_pct_applied"].fillna(0).clip(0, 80)

# normalize channel/status/payment
orders["channel"] = orders["channel"].replace({"In Store":"In-Store", "Instore":"In-Store"})
orders.loc[~orders["channel"].isin(["Online","In-Store"]), "channel"] = "Online"

orders["payment_method"] = orders["payment_method"].fillna("Card")
orders.loc[~orders["payment_method"].isin(["Card","Cash","Digital Wallet"]), "payment_method"] = "Card"

orders["order_status"] = orders["order_status"].fillna("Completed")
orders.loc[~orders["order_status"].isin(["Completed","Returned","Canceled"]), "order_status"] = "Completed"

# remove duplicates (same order_id + product_id + datetime)
orders = orders.drop_duplicates(subset=["order_id","product_id","order_datetime"], keep="first")

# validate foreign keys (store/product must exist; promo optional)
orders = orders[orders["store_id"].isin(stores["store_id"])]
orders = orders[orders["product_id"].isin(products["product_id"])]

# promotion_id: keep NaN, but if not NaN must exist
orders.loc[orders["promotion_id"].notna() & ~orders["promotion_id"].isin(promos["promotion_id"]), "promotion_id"] = np.nan

# add calculated fields (super useful in Power BI)
orders["revenue"] = (orders["units"] * orders["unit_selling_price"]).round(2)

# optional: add COGS + gross margin (premium analytics)
prod_cost = products.set_index("product_id")["cost_price"]
orders["cogs"] = (orders["units"] * orders["product_id"].map(prod_cost)).round(2)
orders["gross_profit"] = (orders["revenue"] - orders["cogs"]).round(2)
orders["gross_margin_pct"] = np.where(orders["revenue"] > 0, (orders["gross_profit"] / orders["revenue"]) * 100, np.nan).round(2)

log("orders_clean", b, len(orders),
    "trim text, parse datetime, enforce numeric bounds, drop invalid rows, dedupe, validate keys, add revenue/cogs/margin")

# -----------------------------
# SAVE CLEAN OUTPUTS
# -----------------------------
products.to_csv("bf_products_clean_2025.csv", index=False)
stores.to_csv("bf_stores_clean_2025.csv", index=False)
promos.to_csv("bf_promotions_clean_2025.csv", index=False)
orders.to_csv("bf_orders_clean_2025.csv", index=False)

pd.DataFrame(quality_log).to_csv("data_quality_report_2025.csv", index=False)

print("CLEAN DONE ✅ Files created:")
print("- bf_products_clean_2025.csv")
print("- bf_stores_clean_2025.csv")
print("- bf_promotions_clean_2025.csv")
print("- bf_orders_clean_2025.csv")
print("- data_quality_report_2025.csv")
print("\nFinal rows:", {
    "products": len(products),
    "stores": len(stores),
    "promotions": len(promos),
    "orders": len(orders)
})


# In[ ]:




