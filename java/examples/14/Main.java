import java.util.*;
public class Main {
    interface Assessment { int points(); }
    static class Exam implements Assessment {
        private final int score;
        Exam(int score) {
            if (score < 0 || score > 100) throw new IllegalArgumentException("score");
            this.score = score;
        }
        public int points() { return score; }
    }
    static boolean passed(Assessment a) { return a.points() >= 50; }
    public static void main(String[] args) {
        List<Assessment> results = List.of(new Exam(49), new Exam(50), new Exam(90));
        System.out.println(results.stream().filter(Main::passed).count());
        if (passed(new Exam(49)) || !passed(new Exam(50))) throw new AssertionError("boundary");
        System.out.println("checks passed");
    }
}
