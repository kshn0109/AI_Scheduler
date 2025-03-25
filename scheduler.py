import json
import random

# JSON 파일을 불러오는 함수
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# 수업 패턴에 맞게 시간대 배정하는 함수
def assign_course_by_pattern(course, professor_name, time_slots, professors_schedule, classrooms):
    pattern = course['pattern']
    course_code = course['course_code']
    assigned_times = []  # 배정된 시간들을 기록할 리스트

    # 강의실을 순환적으로 재사용하는 로직
    assigned_classroom = classrooms.pop(0)  # 첫 번째 강의실을 선택
    classrooms.append(assigned_classroom)  # 강의실을 다시 리스트에 추가하여 순환시킴

    if pattern == "MWF":
        # MWF 패턴은 월, 수, 금에 동일한 시간대 배정
        days = ["Monday", "Wednesday", "Friday"]
        random_day = random.choice(days)  # 랜덤하게 배정될 요일 선택
        available_slots = time_slots[random_day]  # 랜덤 선택할 시간대 목록

        # 랜덤으로 시간대 선택
        selected_slot = random.choice(available_slots)

        for day in days:
            for slot in time_slots[day]:
                if slot == selected_slot and not any(schedule['course'] == course_code for schedule in professors_schedule.get(day, {}).get(slot, [])):
                    professors_schedule.setdefault(day, {}).setdefault(slot, []).append({"course": course_code, "professor": professor_name, "classroom": assigned_classroom})
                    assigned_times.append(f"{day} {slot} - Classroom {assigned_classroom}")
                    break  # 한 수업은 한 시간대에만 배정됨

    elif pattern == "TR":
    # TR 패턴은 화, 목에 연속된 두 시간대를 배정
        days = ["Tuesday", "Thursday"]
        random_day = random.choice(days)  # 랜덤하게 배정될 요일 선택
        available_slots = time_slots[random_day]  # 랜덤 선택할 시간대 목록

    # 연속된 두 시간대를 랜덤으로 선택
        for i in range(len(available_slots) - 1):
            slot1 = random.choice(available_slots)
            slot2 = available_slots[available_slots.index(slot1) + 1] if available_slots.index(slot1) + 1 < len(available_slots) else None

        # slot2가 None이면 다음 루프를 넘김
            if slot2 is None:
                continue

        # 화요일과 목요일에 동일한 시간대가 배정되도록 처리
            if not any(schedule['course'] == course_code for schedule in professors_schedule.get("Tuesday", {}).get(slot1, [])) and \
                not any(schedule['course'] == course_code for schedule in professors_schedule.get("Thursday", {}).get(slot1, [])) and \
                not any(schedule['course'] == course_code for schedule in professors_schedule.get("Tuesday", {}).get(slot2, [])) and \
                not any(schedule['course'] == course_code for schedule in professors_schedule.get("Thursday", {}).get(slot2, [])):

            # 동일한 시간대가 화요일과 목요일에 배정
                professors_schedule.setdefault("Tuesday", {}).setdefault(slot1, []).append({"course": course_code, "professor": professor_name, "classroom": assigned_classroom})
            professors_schedule.setdefault("Thursday", {}).setdefault(slot1, []).append({"course": course_code, "professor": professor_name, "classroom": assigned_classroom})
            professors_schedule.setdefault("Tuesday", {}).setdefault(slot2, []).append({"course": course_code, "professor": professor_name, "classroom": assigned_classroom})
            professors_schedule.setdefault("Thursday", {}).setdefault(slot2, []).append({"course": course_code, "professor": professor_name, "classroom": assigned_classroom})

            # 연속된 두 시간대가 화요일과 목요일에 동일하게 배정되었음을 출력
            assigned_times.append(f"Tuesday {slot1} - {slot2} - Classroom {assigned_classroom}")
            assigned_times.append(f"Thursday {slot1} - {slot2} - Classroom {assigned_classroom}")
            break  # 두 시간대를 연속적으로 배정하고 종료

            
    elif pattern == "single_day_3hrs":
        # 3시간 연속 배정은 하나의 요일에 3시간을 나눠서 배정
        days = ["Monday"]  # 예시로 월요일에 배정한다고 가정
        random_day = random.choice(days)  # 랜덤하게 배정될 요일 선택
        slots = time_slots[random_day]
        
        # 3시간 연속 배정할 수 있는 시간대 찾기
        for i in range(len(slots) - 2):  # 3시간 연속 배정
            if all(slots[i + j] not in assigned_times for j in range(3)):
                for j in range(3):  # 3시간 연속 배정
                    professors_schedule.setdefault(random_day, {}).setdefault(slots[i + j], []).append({"course": course_code, "professor": professor_name, "classroom": assigned_classroom})
                    assigned_times.append(f"{random_day} {slots[i + j]} - Classroom {assigned_classroom}")
                break  # 3시간 연속 배정이 완료되면 중단

    return assigned_times, professors_schedule


# JSON 파일 불러오기
time_slots_data = load_json('time_slots.json')
time_slots = time_slots_data["time_slots"]  # "time_slots" 키에서 시간대 데이터를 가져옵니다.

classrooms_data = load_json('classrooms.json')
classrooms = classrooms_data['classrooms']  # 교실 목록

professors_data = load_json('professors.json')  # 교수 정보

# 교수와 수업 정보
professors_schedule = {}  # 교수별로 배정된 시간표를 기록할 딕셔너리
courses = []
for professor, details in professors_data.items():
    for course in details['courses']:
        courses.append((course, professor))  # 수업과 교수 이름을 함께 리스트에 추가

# 수업 배정
professor_assignments = {}  # 교수별 배정된 수업 시간 저장

for course, professor_name in courses:
    assigned_times, professors_schedule = assign_course_by_pattern(course, professor_name, time_slots, professors_schedule, classrooms)

    # 교수 이름별로 배정된 수업 시간들을 저장
    if professor_name not in professor_assignments:
        professor_assignments[professor_name] = []

    professor_assignments[professor_name].append((course['course_code'], assigned_times))

# 출력: 교수별로 수업 시간 정렬 후 출력
for professor_name, assignments in professor_assignments.items():
    print(f"Assigned times for {professor_name}:")
    for course_code, times in sorted(assignments, key=lambda x: x[0]):  # 수업 코드 순으로 정렬
        print(f"  Course: {course_code}")
        for time in times:
            print(f"    {time}")
    print()  # 교수별로 한 줄 띄우기
