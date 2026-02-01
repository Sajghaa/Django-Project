from django.shortcuts import render

def home(request):
    context ={
        'name': "Serge Developer",
        'bio' : 'I’m a Django Developer who loves building projects to learn and grow.',
        'skills' : ['Python', 'Django','HTML', 'CSS', 'JavaScript', 'React', 'Typescript']
    }

    return render(request, 'portfolio/home.html', context)

def projects(request):
    project_list =[
        {'title': 'Weather App', 'description' : 'A weather forecast web pp.'},
        {'title': 'To-Do List', 'description': 'An app to manage daily tasks.'},
        {'title': 'Notes App', 'description': 'Keep your notes organized.'}
    ]

    return render(request, 'portfolio/projects.html', {'projects': project_list})

def contact(request):
    return render(request, 'portfolio/contact.html')