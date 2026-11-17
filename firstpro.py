"""
Project: Academic Performance & Grade Management System
Author: Professional Python Portfolio Project
Description: An Object-Oriented CLI application for managing student records,
             calculating 4.0 scale GPAs, generating leaderboards, and persisting data via JSON.
"""

import json
import os
from typing import Dict, Any, List

class Student:
    """Represents an individual student and handles academic calculations."""
    
    def __init__(self, roll_no: str, name: str, marks: Dict[str, float] = None):
        self.roll_no = roll_no
        self.name = name
        self.marks = marks or {}

    def calculate_total(self) -> float:
        """Returns total accumulated marks across all subjects."""
        return sum(self.marks.values()) if self.marks else 0.0

    def calculate_average(self) -> float:
        """Returns percentage average of marks."""
        if not self.marks:
            return 0.0
        return self.calculate_total() / len(self.marks)

    @staticmethod
    def _get_gpa_points(marks: float) -> float:
        """Converts individual subject percentage to 4.0 scale points."""
        if marks >= 90: return 4.0
        elif marks >= 80: return 3.7
        elif marks >= 70: return 3.0
        elif marks >= 60: return 2.0
        elif marks >= 50: return 1.0
        else: return 0.0

    def calculate_gpa(self) -> float:
        """Calculates cumulative GPA on a standard 4.0 scale."""
        if not self.marks:
            return 0.0
        total_points = sum(self._get_gpa_points(m) for m in self.marks.values())
        return total_points / len(self.marks)

    def calculate_grade(self) -> str:
        """Determines overall letter grade based on average percentage."""
        avg = self.calculate_average()
        if avg >= 90: return "A+"
        elif avg >= 80: return "A"
        elif avg >= 70: return "B"
        elif avg >= 60: return "C"
        elif avg >= 50: return "D"
        else: return "F"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes student object to a dictionary for JSON storage."""
        return {
            "name": self.name,
            "marks": self.marks
        }


class GradeManagementSystem:
    """Manages the database, file persistence, and user interaction loop."""
    
    def __init__(self, filename: str = "school_database.json"):
        self.filename = filename
        self.students: Dict[str, Student] = {}
        self.load_database()

    def load_database(self) -> None:
        """Loads student records from local JSON storage if available."""
        if not os.path.exists(self.filename):
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                for roll, info in raw_data.items():
                    self.students[roll] = Student(roll, info["name"], info["marks"])
        except (json.JSONDecodeError, IOError):
            print("[!] Warning: Database corrupted or unreadable. Initializing empty state.")

    def save_database(self) -> None:
        """Persists current student records to disk via JSON."""
        try:
            data = {roll: student.to_dict() for roll, student in self.students.items()}
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except IOError:
            print("[!] Error: Failed to save database to disk.")

    def add_student(self) -> None:
        """Registers a new student and their subject marks."""
        print("\n--- Register New Student ---")
        roll_no = input("Enter Unique Roll Number: ").strip()
        if not roll_no:
            print("[!] Roll number cannot be empty.\n")
            return
        if roll_no in self.students:
            print(f"[!] Error: Student with Roll Number '{roll_no}' already exists!\n")
            return

        name = input("Enter Student Full Name: ").strip()
        if not name:
            print("[!] Name cannot be empty.\n")
            return

        subjects = {}
        try:
            num_subs = int(input("Enter number of subjects: "))
            if num_subs <= 0:
                print("[!] Must have at least 1 subject.\n")
                return
        except ValueError:
            print("[!] Invalid numerical input.\n")
            return

        for _ in range(num_subs):
            sub_name = input("  -> Subject name: ").strip()
            if not sub_name:
                sub_name = "General"
            while True:
                try:
                    marks = float(input(f"     Marks for {sub_name} (0-100): "))
                    if 0 <= marks <= 100:
                        subjects[sub_name] = marks
                        break
                    print("     [!] Marks must be between 0 and 100.")
                except ValueError:
                    print("     [!] Please enter a valid number.")

        self.students[roll_no] = Student(roll_no, name, subjects)
        self.save_database()
        print(f"[+] Success: Student '{name}' registered successfully!\n")

    def view_report_card(self) -> None:
        """Displays a detailed report card for a specific student."""
        print("\n--- Student Report Card ---")
        roll_no = input("Enter Roll Number: ").strip()
        if roll_no not in self.students:
            print("[!] Student not found in database.\n")
            return

        student = self.students[roll_no]
        print("\n" + "=" * 45)
        print(f" REPORT CARD: {student.name.upper()} (Roll: {roll_no})")
        print("=" * 45)

        if not student.marks:
            print(" No marks recorded.")
        else:
            for sub, score in student.marks.items():
                print(f"   • {sub:<18} : {score:>5.1f} / 100")
            print("-" * 45)
            print(f"   Total Marks      : {student.calculate_total():>5.1f}")
            print(f"   Percentage       : {student.calculate_average():>5.2f}%")
            print(f"   GPA (4.0 Scale)  : {student.calculate_gpa():>5.2f} / 4.0")
            print(f"   Overall Grade    : {student.calculate_grade():>5}")
        print("=" * 45 + "\n")

    def update_marks(self) -> None:
        """Updates marks for an existing student record."""
        print("\n--- Update Student Records ---")
        roll_no = input("Enter Roll Number to update: ").strip()
        if roll_no not in self.students:
            print("[!] Student not found.\n")
            return

        student = self.students[roll_no]
        print(f"Updating record for: {student.name}")
        print("Current subjects and marks:")
        for sub, score in student.marks.items():
            print(f"   - {sub}: {score}")

        sub_name = input("Enter subject name to update/add: ").strip()
        if not sub_name:
            print("[!] Invalid subject name.\n")
            return

        while True:
            try:
                new_marks = float(input(f"Enter new marks for {sub_name} (0-100): "))
                if 0 <= new_marks <= 100:
                    student.marks[sub_name] = new_marks
                    self.save_database()
                    print(f"[+] Success: Marks updated for {student.name}!\n")
                    break
                print("[!] Marks must be between 0 and 100.")
            except ValueError:
                print("[!] Please enter a valid number.")

    def delete_student(self) -> None:
        """Removes a student record from the system."""
        print("\n--- Delete Student Record ---")
        roll_no = input("Enter Roll Number to delete: ").strip()
        if roll_no not in self.students:
            print("[!] Student not found.\n")
            return

        name = self.students[roll_no].name
        confirm = input(f"Are you sure you want to delete {name} (Roll: {roll_no})? (y/n): ").strip().lower()
        if confirm == 'y':
            del self.students[roll_no]
            self.save_database()
            print(f"[+] Success: Record for {name} deleted.\n")
        else:
            print("[*] Deletion cancelled.\n")

    def view_leaderboard(self) -> None:
        """Renders a ranked performance leaderboard of all students."""
        if not self.students:
            print("\n[!] No student records available to rank.\n")
            return

        sorted_students = sorted(
            self.students.values(),
            key=lambda s: s.calculate_total(),
            reverse=True
        )

        print("\n" + "=" * 62)
        print(f" {'CLASS ACADEMIC LEADERBOARD (RANKINGS)':^58} ")
        print("=" * 62)
        print(f"{'Rank':<6} {'Roll No':<10} {'Name':<18} {'Total':<9} {'GPA':<6} {'Grade':<6}")
        print("-" * 62)

        for rank, student in enumerate(sorted_students, 1):
            print(
                f"{rank:<6} "
                f"{student.roll_no:<10} "
                f"{student.name:<18} "
                f"{student.calculate_total():<9.1f} "
                f"{student.calculate_gpa():<6.2f} "
                f"{student.calculate_grade():<6}"
            )
        print("=" * 62 + "\n")

    def run(self) -> None:
        """Main application runner loop."""
        while True:
            print("==========================================")
            print("     MARKS & GRADE MANAGEMENT SYSTEM      ")
            print("==========================================")
            print("1. Register New Student")
            print("2. View Student Report Card")
            print("3. Update Student Marks")
            print("4. Delete Student Record")
            print("5. View Class Leaderboard / Rankings")
            print("6. Exit Application")
            print("------------------------------------------")

            choice = input("Select an option (1-6): ").strip()

            if choice == '1':
                self.add_student()
            elif choice == '2':
                self.view_report_card()
            elif choice == '3':
                self.update_marks()
            elif choice == '4':
                self.delete_student()
            elif choice == '5':
                self.view_leaderboard()
            elif choice == '6':
                print("\nThank you for using the Grade Management System. Goodbye!\n")
                break
            else:
                print("[!] Invalid selection. Please choose a number between 1 and 6.\n")


if __name__ == "__main__":
    app = GradeManagementSystem()
    app.run()