public class Main {
    static int score(String value) {
        int n = Integer.parseInt(value);
        if (n < 0 || n > 100) throw new IllegalArgumentException("range");
        return n;
    }
    public static void main(String[] args) {
        try { System.out.println(score("75")); }
        catch (IllegalArgumentException e) { System.out.println("invalid"); }
        finally { System.out.println("done"); }
    }
}
