from django.shortcuts import render

history = []

def home(request):
    result = ''
    if request.method == 'POST':
        num1 = request.POST.get('num1')
        num2 = request.POST.get('num2')
        operation = request.POST.get('operation')

        if num1 and num2:
            num1 = float(num1)
            num2 = float(num2)
            if operation == 'add':
                result = num1 + num2
                symbol = '+'
            elif operation == 'subtract':
                result = num1 - num2
                symbol = '-'
            elif operation == 'multiply':
                result = num1 * num2
                symbol = '×'
            elif operation == 'divide':
                if num2 != 0:
                    result = num1 / num2
                else:
                    result = 'Error: Division by 0'
                symbol = '÷'
            
            history.insert(0, f"{num1} {symbol} {num2} = {result}")
            if len(history) > 10:  # keep last 10
                history.pop()

    return render(request, 'calculator/home.html', {'result': result, 'history': history})
