package io.oisin.fyp.model;

import com.google.android.gms.maps.model.Polyline;

import java.util.List;

/**
 * Created by Oisin Quinn (@oisin1001) on 2020-03-11.
 */
public class RouteType {
    private Polyline polyline;
    private double distance;
    private double duration;
    private double calories;
    private double co2saved;
    private List<Direction> directions;

    public RouteType(Polyline polyline, double distance, double duration, double calories,
                     double co2saved, List<Direction> directions) {
        this.polyline = polyline;
        this.distance = distance;
        this.duration = duration;
        this.calories = calories;
        this.co2saved = co2saved;
        this.directions = directions;
    }

    public Polyline getPolyline() {
        return polyline;
    }

    public double getDistance() {
        return distance;
    }

    public double getDuration() {
        return duration;
    }

    public double getCalories() {
        return calories;
    }

    public double getCo2saved() {
        return co2saved;
    }

    public List<Direction> getDirections() {
        return directions;
    }
}
