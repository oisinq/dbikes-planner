package io.oisin.fyp.model;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;

/**
 * Created by Oisin Quinn (@oisin1001) on 2020-03-11.
 */
public class Direction {
    private String direction;
    private double distance;
    private double time;
    private String name;

    public Direction(String direction, double distance, double time, String name) {
        this.direction = direction;
        this.distance = distance;
        this.time = time;
        this.name = name;
    }

    public String getDirection() {
        return direction;
    }

    public void setDirection(String direction) {
        this.direction = direction;
    }

    public double getDistance() {
        return distance;
    }

    public void setDistance(double distance) {
        this.distance = distance;
    }

    public double getTime() {
        return time;
    }

    public void setTime(double time) {
        this.time = time;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public static ArrayList<Direction> createDirectionList(int numDirections) {
        ArrayList<Direction> directions = new ArrayList<>();

        ArrayList<String> directionStrings = new ArrayList<>(
                Arrays.asList("bear right", "bear left", "turn right", "turn left", "sharp right", "sharp left", "straight on"));

        for (int i = 1; i <= numDirections; i++) {
            directions.add(new Direction(directionStrings.get(new Random().nextInt(directionStrings.size())), new Random().nextInt(1500), new Random().nextInt(9), "Main St"));
        }

        return directions;
    }
}

//case "bear right":
//        return R.drawable.bear_right_arrow;
//        case "bear left":
//        return R.drawable.bear_left_arrow;
//        case "turn right":
//        case "sharp right":
//        return R.drawable.right_arrow;
//        case "turn left":
//        case "sharp left":
//        return R.drawable.left_arrow;
//        case "straight on":