#用packge替代module

import edu


def main():
    height:int = int(input("請輸入身高(cm):"))
    weight:int = int(input("請輸入體重(kg):"))

    bmi = edu.tools. caculate_bmi(height, weight)

    print(bmi)
    print(edu.tools. get_state(bmi))


if __name__ == '__main__':
    main()