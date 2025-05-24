#自訂的function 目的是結構化程式碼
#自訂的moudle, package 目的是結構化專案
#一個package裡有多個module 一個module裡有多個function

# 用impprt module 結構化程式碼
import tools

def main():
    height:int = int(input("請輸入身高(cm):"))
    weight:int = int(input("請輸入體重(kg):"))

    bmi = tools.caculate_bmi(height, weight)

    print(bmi)
    print(tools.get_state(bmi))


if __name__ == '__main__':
    main()