iurl = "https://www.amazon.in/dp/B0791YHVMK/ref=cm_sw_r_cp_apa_i_WihKFbBPHPCN0"
storeProductId = ""
try:
    storeProductId = iurl.split("/dp/")[1].split("/")[0].split('?')[0]
except:
    storeProductId = iurl.split("/dp/")[1].split("/")[0]

print(storeProductId)