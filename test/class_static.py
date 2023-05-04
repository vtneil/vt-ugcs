class A:
    class X:
        pass
    ref_cnt = 0

    def __init__(self):
        pass

    @classmethod
    def increment(cls):
        cls.ref_cnt += 1


if __name__ == '__main__':
    A.ref_cnt += 1

    a1 = A()
    a2 = A()

    print(A.ref_cnt)

    a1.increment()
    print(A.ref_cnt)

    a2.increment()
    print(A.ref_cnt)


