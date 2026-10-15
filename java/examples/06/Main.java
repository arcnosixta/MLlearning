public class Main {
    static class Person {
        String role() { return "person"; }
    }
    static class Student extends Person {
        @Override String role() { return "student"; }
    }
    public static void main(String[] args) {
        Person person = new Student();
        System.out.println(person.role());
    }
}
