from dhanhq import dhanhq
import pandas as pd
import time

dhan = dhanhq("9884383177","eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzAxMTAwMzU5LCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTEwMDY0MDMxNyJ9.D-goOfdSBSCA3K2zZnbGTqMexLcHpGM3jki3VzJlpWUoGBQ31rLEUkYeIuo_P34ttdQ5Iol12RujHpLrJpzhJQ")
print(dhan.get_positions())
# def close_positions():
#        net_pos = dhan.get_positions()
#        if net_pos['data'] is not None:
#             for o in net_pos['data']:
#                 if int(o['netQty']) != 0:
#                     direction = "SELL" if int(o['netQty']) > 0 else "BUY"
#                     print("Its entered here")
#                     print (o["tradingSymbol"])
#                     print(direction)
#                     print(o['securityId'])
#                     print(abs(int(o['netQty'])))
#                     # dhan.place_order(security_id=o['securityId'], 
#                     #     exchange_segment=dhan.FNO,
#                     #     transaction_type=dhan.SELL,
#                     #     quantity=o['netQty'],
#                     #     order_type=dhan.MARKET,
#                     #     product_type=dhan.INTRA,
#                     #     price=0)         
#                     place_order(o['securityId'],dhan.FNO,dhan.SELL,o['netQty'],dhan.MARKET,dhan.INTRA,price=0)           
#                     print("Closed  position successfully")
#                     time.sleep(0.2)
#             print("No position to close")

# def place_order(security_id,exchange_seg,type,qty,o_type,p_type,price):
#     dhan.place_order(security_id=security_id, 
#                         exchange_segment=exchange_seg,
#                         transaction_type=type,
#                         quantity=qty,
#                         order_type=o_type,
#                         product_type=p_type,
#                         price=price)
#     print("Order placed successfully")
    
# close_positions() 
# print(dhan.get_order_list() )
