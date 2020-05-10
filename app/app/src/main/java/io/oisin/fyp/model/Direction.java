package io.oisin.fyp.model;

/**
 * Created by Oisin Quinn (@oisin1001) on 2020-03-11.
 *
 * Signifies a single direction in a row of the DirectionsAdapter
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

    public double getDistance() {
        return distance;
    }

    public double getTime() {
        return time;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}