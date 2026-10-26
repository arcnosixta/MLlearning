import java.awt.*;
import java.awt.image.BufferedImage;
import javax.swing.*;
public class Main {
    static void window() {
        JFrame frame = new JFrame("Java course");
        frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        JLabel label = new JLabel("0", SwingConstants.CENTER);
        JButton button = new JButton("+1");
        int[] count = {0}; // Both listener and initialization run on the EDT.
        button.addActionListener(event -> label.setText(Integer.toString(++count[0])));
        frame.add(label, BorderLayout.CENTER);
        frame.add(button, BorderLayout.SOUTH);
        frame.setPreferredSize(new Dimension(300, 180));
        frame.pack();
        frame.setLocationByPlatform(true);
        frame.setVisible(true);
    }
    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("--window")) {
            SwingUtilities.invokeLater(Main::window);
            return;
        }
        BufferedImage image = new BufferedImage(20, 20, BufferedImage.TYPE_INT_RGB);
        Graphics2D graphics = image.createGraphics();
        try {
            graphics.setColor(Color.BLUE);
            graphics.fillRect(0, 0, 20, 20);
        } finally { graphics.dispose(); }
        System.out.println(image.getRGB(10, 10) == Color.BLUE.getRGB());
    }
}
