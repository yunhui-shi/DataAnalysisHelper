def generate_fibonacci(n):
    """生成斐波那契数列
    
    参数:
        n (int): 要生成的斐波那契数列的长度
        
    返回:
        list: 包含前n个斐波那契数的列表
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_num = fib_sequence[-1] + fib_sequence[-2]
        fib_sequence.append(next_num)
    
    return fib_sequence

if __name__ == "__main__":
    try:
        length = int(input("请输入要生成的斐波那契数列的长度: "))
        result = generate_fibonacci(length)
        print(f"前{length}个斐波那契数列是: {result}")
    except ValueError:
        print("请输入一个有效的整数!")
