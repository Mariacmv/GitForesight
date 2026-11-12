
PLANS = {
    "explorar": {
        "name": "Explorar",
        "price_monthly": 0,
        "limits": {
            "repositories": 1,
            "members": 1,
        },
        "features": {
            "overview": True,
            "heatmap": "full",
            "predictive": "full",
            "simulations": False,
            "pdf_export": False,
            "full_history": False,
            "team_management": False,
            "repository_comparison": False,
        },
    },

    "equipe": {
        "name": "Equipe",
        "price_monthly": 149,
        "limits": {
            "repositories": 5,
            "members": 10,
        },
        "features": {
            "overview": True,
            "heatmap": "full",
            "predictive": "full",
            "simulations": True,
            "pdf_export": True,
            "full_history": True,
            "team_management": True,
            "repository_comparison": True,
        },
    },

    "organizacao": {
        "name": "Organização",
        "price_monthly": None,
        "limits": {
            "repositories": None,
            "members": None,
        },
        "features": {
            "overview": True,
            "heatmap": "full",
            "predictive": "full",
            "simulations": True,
            "pdf_export": True,
            "full_history": True,
            "team_management": True,
            "repository_comparison": True,
        },
    },
}

def get_plan(plan_key):
    return PLANS.get(plan_key, PLANS["explorar"])


def get_plan_limit(plan_key, limit):
    return get_plan(plan_key)["limits"].get(limit)


def get_plan_feature(plan_key, feature):
    return get_plan(plan_key)["features"].get(feature, False)
