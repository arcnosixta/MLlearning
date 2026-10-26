public class Main {
    enum State { START, ZERO, ACCEPT }
    static boolean accepts(String input) {
        State state = State.START;
        for (char symbol : input.toCharArray()) {
            if (symbol != '0' && symbol != '1') return false;
            state = switch (state) {
                case START -> symbol == '0' ? State.ZERO : State.START;
                case ZERO -> symbol == '0' ? State.ZERO : State.ACCEPT;
                case ACCEPT -> symbol == '0' ? State.ZERO : State.START;
            };
        }
        return state == State.ACCEPT;
    }
    public static void main(String[] args) {
        System.out.println(accepts("101"));
        System.out.println(accepts("010"));
        System.out.println(accepts(""));
        System.out.println(accepts("01x"));
    }
}
