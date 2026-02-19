"""
02_property_setter.py
주제:
- property
- setter
- 값 검증
"""

class BankAccount:

    def __init__(self, owner, balance):
        self.owner = owner
        self._balance = 0
        self.balance = balance  # setter를 통하도록

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        """
        TODO:
        - value가 int가 아니면 TypeError 발생
        - 0보다 작으면 ValueError 발생
        """
        try:
            if int(value) < 0:
                raise ValueError
            else:  
                self._balance = value # 현재는 검증이 없음 (일부러 틀림)
        except:
            raise ValueError
      

    def deposit(self, amount):
        self.balance += amount


if __name__ == "__main__":
    acc = BankAccount("홍길동", 1000)
    acc.deposit(500)
    print(acc.balance)

    # 아래를 통과하지 못하도록 수정하세요
    acc.balance = 100
    acc.deposit(500)
    print(acc.balance)