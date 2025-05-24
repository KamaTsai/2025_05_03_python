#用__name__ & __main__將主程式也用function 整合，全部整合完成才是完整的執行檔
# Python 在執行任何程式碼時，都會自動定義一些特殊的內建變數。其中一個就是 __name__。
# 當檔案被直接執行時：Python 會自動將這個檔案的 __name__ 變數設置為字串 '__main__'。 所以，當 if __name__ == '__main__': 這個條件成立時，就表示這個檔案是當前被執行的主程式。

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
def main():
    height:int = int(input("請輸入身高(CM):"))
    Weight:int = int(input("請輸入體重(KG):"))
    bmi = caculate_bmi(height,Weight)
    print("你的BMI:",bmi)
    print(get_state(bmi))
if __name__ == '__main__':
    main()