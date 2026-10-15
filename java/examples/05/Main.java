public class Main {
    static class Student {
        private final String name;
        private int points;
        Student(String name) { this.name = name; }
        void addPoints(int value) {
            if (value < 0) throw new IllegalArgumentException("negative");
            points += value;
        }
        String report() { return name + ": " + points; }
    }
    public static void main(String[] args) {
        Student student = new Student("Aida");
        student.addPoints(20);
        System.out.println(student.report());
    }
}
