import java.util.*;
public class Main {
    public static OptionalDouble average(List<Integer> grades) {
        Objects.requireNonNull(grades);
        long total = 0;
        for (Integer grade : grades) {
            if (grade == null || grade < 0 || grade > 100) throw new IllegalArgumentException("grade 0..100 required");
            total += grade;
        }
        return grades.isEmpty() ? OptionalDouble.empty() : OptionalDouble.of((double) total / grades.size());
    }
    public static void main(String[] args) {
        if (average(List.of(2, 3)).orElseThrow() != 2.5) throw new AssertionError("fraction");
        if (average(List.of()).isPresent()) throw new AssertionError("empty");
        try { average(List.of(101)); throw new AssertionError("range"); }
        catch (IllegalArgumentException expected) { /* Required rejection. */ }
        System.out.println("checks=3");
        System.out.println(average(List.of(80, 90)).orElseThrow());
    }
}
