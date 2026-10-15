import java.util.*;
public class Main {
    static final class Student {
        private final int id;
        Student(int id) { this.id = id; }
        @Override public boolean equals(Object other) {
            return other instanceof Student && id == ((Student) other).id;
        }
        @Override public int hashCode() { return Integer.hashCode(id); }
    }
    public static void main(String[] args) {
        Set<Student> students = new HashSet<>();
        students.add(new Student(1));
        students.add(new Student(1));
        System.out.println(students.size());
    }
}
