"""
Copyright (C) 2018 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""

"""
The known server versions.
"""

#MIN_SERVER_VER_REAL_TIME_BARS       = 34
#MIN_SERVER_VER_SCALE_ORDERS         = 35
#MIN_SERVER_VER_SNAPSHOT_MKT_DATA    = 35
#MIN_SERVER_VER_SSHORT_COMBO_LEGS    = 35
#MIN_SERVER_VER_WHAT_IF_ORDERS       = 36
#MIN_SERVER_VER_CONTRACT_CONID       = 37
MIN_SERVER_VER_PTA_ORDERS             = 39
MIN_SERVER_VER_FUNDAMENTAL_DATA       = 40
MIN_SERVER_VER_DELTA_NEUTRAL          = 40
MIN_SERVER_VER_CONTRACT_DATA_CHAIN    = 40
MIN_SERVER_VER_SCALE_ORDERS2          = 40
MIN_SERVER_VER_ALGO_ORDERS            = 41
MIN_SERVER_VER_EXECUTION_DATA_CHAIN   = 42
MIN_SERVER_VER_NOT_HELD               = 44
MIN_SERVER_VER_SEC_ID_TYPE            = 45
MIN_SERVER_VER_PLACE_ORDER_CONID      = 46
MIN_SERVER_VER_REQ_MKT_DATA_CONID     = 47
MIN_SERVER_VER_REQ_CALC_IMPLIED_VOLAT = 49
MIN_SERVER_VER_REQ_CALC_OPTION_PRICE  = 50
MIN_SERVER_VER_SSHORTX_OLD            = 51
MIN_SERVER_VER_SSHORTX                = 52
MIN_SERVER_VER_REQ_GLOBAL_CANCEL      = 53
MIN_SERVER_VER_HEDGE_ORDERS           = 54
MIN_SERVER_VER_REQ_MARKET_DATA_TYPE   = 55
MIN_SERVER_VER_OPT_OUT_SMART_ROUTING  = 56
MIN_SERVER_VER_SMART_COMBO_ROUTING_PARAMS = 57
MIN_SERVER_VER_DELTA_NEUTRAL_CONID    = 58
MIN_SERVER_VER_SCALE_ORDERS3          = 60
MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE = 61
MIN_SERVER_VER_TRAILING_PERCENT       = 62
MIN_SERVER_VER_DELTA_NEUTRAL_OPEN_CLOSE = 66
MIN_SERVER_VER_POSITIONS              = 67
MIN_SERVER_VER_ACCOUNT_SUMMARY        = 67
MIN_SERVER_VER_TRADING_CLASS          = 68
MIN_SERVER_VER_SCALE_TABLE            = 69
MIN_SERVER_VER_LINKING                = 70
MIN_SERVER_VER_ALGO_ID                = 71
MIN_SERVER_VER_OPTIONAL_CAPABILITIES  = 72
MIN_SERVER_VER_ORDER_SOLICITED        = 73
MIN_SERVER_VER_LINKING_AUTH           = 74
MIN_SERVER_VER_PRIMARYEXCH            = 75
MIN_SERVER_VER_RANDOMIZE_SIZE_AND_PRICE = 76
MIN_SERVER_VER_FRACTIONAL_POSITIONS   = 101
MIN_SERVER_VER_PEGGED_TO_BENCHMARK    = 102
MIN_SERVER_VER_MODELS_SUPPORT         = 103
MIN_SERVER_VER_SEC_DEF_OPT_PARAMS_REQ = 104
MIN_SERVER_VER_EXT_OPERATOR           = 105
MIN_SERVER_VER_SOFT_DOLLAR_TIER       = 106
MIN_SERVER_VER_REQ_FAMILY_CODES       = 107
MIN_SERVER_VER_REQ_MATCHING_SYMBOLS   = 108
MIN_SERVER_VER_PAST_LIMIT             = 109
MIN_SERVER_VER_MD_SIZE_MULTIPLIER     = 110
MIN_SERVER_VER_CASH_QTY               = 111
MIN_SERVER_VER_REQ_MKT_DEPTH_EXCHANGES = 112
MIN_SERVER_VER_TICK_NEWS              = 113
MIN_SERVER_VER_REQ_SMART_COMPONENTS   = 114
MIN_SERVER_VER_REQ_NEWS_PROVIDERS     = 115
MIN_SERVER_VER_REQ_NEWS_ARTICLE       = 116
MIN_SERVER_VER_REQ_HISTORICAL_NEWS    = 117
MIN_SERVER_VER_REQ_HEAD_TIMESTAMP     = 118
MIN_SERVER_VER_REQ_HISTOGRAM          = 119
MIN_SERVER_VER_SERVICE_DATA_TYPE      = 120
MIN_SERVER_VER_AGG_GROUP              = 121
MIN_SERVER_VER_UNDERLYING_INFO        = 122
MIN_SERVER_VER_CANCEL_HEADTIMESTAMP   = 123
MIN_SERVER_VER_SYNT_REALTIME_BARS     = 124
MIN_SERVER_VER_CFD_REROUTE            = 125
MIN_SERVER_VER_MARKET_RULES           = 126
MIN_SERVER_VER_PNL                    = 127
MIN_SERVER_VER_NEWS_QUERY_ORIGINS     = 128
MIN_SERVER_VER_UNREALIZED_PNL         = 129
MIN_SERVER_VER_HISTORICAL_TICKS       = 130
MIN_SERVER_VER_MARKET_CAP_PRICE       = 131
MIN_SERVER_VER_PRE_OPEN_BID_ASK       = 132
MIN_SERVER_VER_REAL_EXPIRATION_DATE   = 134
MIN_SERVER_VER_REALIZED_PNL           = 135
MIN_SERVER_VER_LAST_LIQUIDITY         = 136
MIN_SERVER_VER_TICK_BY_TICK           = 137
MIN_SERVER_VER_DECISION_MAKER         = 138
MIN_SERVER_VER_MIFID_EXECUTION        = 139
MIN_SERVER_VER_TICK_BY_TICK_IGNORE_SIZE = 140
MIN_SERVER_VER_AUTO_PRICE_FOR_HEDGE     = 141
MIN_SERVER_VER_WHAT_IF_EXT_FIELDS       = 142
MIN_SERVER_VER_SCANNER_GENERIC_OPTS     = 143
MIN_SERVER_VER_API_BIND_ORDER           = 144
MIN_SERVER_VER_ORDER_CONTAINER          = 145
MIN_SERVER_VER_SMART_DEPTH              = 146
MIN_SERVER_VER_REMOVE_NULL_ALL_CASTING  = 147
MIN_SERVER_VER_D_PEG_ORDERS             = 148

# 100+ messaging */
# 100 = enhanced handshake, msg length prefixes

MIN_CLIENT_VER = 100
MAX_CLIENT_VER = MIN_SERVER_VER_D_PEG_ORDERS
