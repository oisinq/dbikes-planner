package io.oisin.fyp.model;

import com.google.android.gms.maps.model.Polyline;

import java.util.List;

/**
 * Data class used to signify an individual route.
 * Created by Oisin Quinn (@oisin1001) on 2020-03-11.
 */
public class RouteType {
    private Polyline polyline;
    private double cyclingDistance;
    private double walkingDistance;
    private double cyclingDuration;
    private double walkingDuration;
    private double calories;
    private double co2saved;
    private List<Direction> directions;

    public RouteType(Polyline polyline, double cyclingDistance, double walkingDistance, double cyclingDuration,
                     double walkingDuration, double calories, double co2saved, List<Direction> directions) {
        this.polyline = polyline;
        this.cyclingDistance = cyclingDistance;
        this.walkingDistance = walkingDistance;
        this.cyclingDuration = cyclingDuration;
        this.walkingDuration = walkingDuration;
        this.calories = calories;
        this.co2saved = co2saved;
        this.directions = directions;
    }

    public Polyline getPolyline() {
        return polyline;
    }

    public double getCyclingDistance() {
        return cyclingDistance;
    }

    public double getWalkingDistance() {
        return walkingDistance;
    }

    public double getTotalDistance() {
        return walkingDistance + cyclingDistance;
    }

    public double getCyclingDuration() {
        return cyclingDuration;
    }

    public double getWalkingDuration() {
        return walkingDuration;
    }

    public double getTotalDuration() {
        return walkingDuration + cyclingDuration;
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
