def fibonacci(n):
    """生成斐波那契数列前n项"""
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

if __name__ == "__main__":
    # 示例：打印前10项斐波那契数列
    print(fibonacci(10))
