package io.oisin.fyp.model;

import com.google.android.gms.maps.model.Polyline;

/**
 * Created by Oisin Quinn (@oisin1001) on 2020-03-11.
 */
public class RouteType {
    private Polyline polyline;
    private double distance;
    private double duration;
    private double calories;
    private double co2saved;

    public RouteType(Polyline polyline, double distance, double duration, double calories, double co2saved) {
        this.polyline = polyline;
        this.distance = distance;
        this.duration = duration;
        this.calories = calories;
        this.co2saved = co2saved;
    }

    public Polyline getPolyline() {
        return polyline;
    }

    public void setPolyline(Polyline polyline) {
        this.polyline = polyline;
    }

    public double getDistance() {
        return distance;
    }

    public void setDistance(double distance) {
        this.distance = distance;
    }

    public double getDuration() {
        return duration;
    }

    public void setDuration(double duration) {
        this.duration = duration;
    }

    public double getCalories() {
        return calories;
    }

    public void setCalories(double calories) {
        this.calories = calories;
    }

    public double getCo2saved() {
        return co2saved;
    }

    public void setCo2saved(double co2saved) {
        this.co2saved = co2saved;
    }
}
