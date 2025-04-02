def fibonacci(n):
    """生成斐波那契数列前n项"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])
    return sequence

if __name__ == "__main__":
    # 示例用法
    print(fibonacci(10))  # 打印前10项
