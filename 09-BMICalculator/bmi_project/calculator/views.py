from django.shortcuts import render

def bmi_calculator(request):
    bmi = None
    category = None

    if request.method == "POST":
        try:
            weight = float(request.POST.get("weight"))
            height = float(request.POST.get("height")) / 100  # convert cm → m
            bmi = round(weight / (height ** 2), 2)

            if bmi < 18.5:
                category = "Underweight"
            elif 18.5 <= bmi < 24.9:
                category = "Normal weight"
            elif 25 <= bmi < 29.9:
                category = "Overweight"
            else:
                category = "Obesity"

        except (ValueError, ZeroDivisionError):
            category = "Invalid input! Please check your values."

    return render(request, "calculator/bmi.html", {"bmi": bmi, "category": category})
