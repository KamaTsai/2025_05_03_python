def caculate_bmi(height:int,Weight:int)->float:
    return Weight/(height/100)**2
def get_state(bmi:float)->str:
    if bmi<18.5:
        return "體重過輕"
    elif bmi<24:
        return"體重正常"
    elif bmi<27:
        return"體重過重"
    elif bmi<30:
        return"輕度肥胖"
    elif bmi<35:
        return"中度肥胖"
    else:
        return"重度肥胖"