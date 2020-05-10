package io.oisin.fyp;

import com.google.android.gms.maps.model.LatLng;
import com.google.maps.android.clustering.ClusterItem;

public class StationClusterItem implements ClusterItem {
    private final LatLng mPosition;
    private String mTitle;
    private String mSnippet;
    private boolean isStartStation = false;
    private boolean isEndStation = false;
    private int availableBikes;
    private int totalSpaces;

    StationClusterItem(double lat, double lng, String title, String snippet, int availableBikes, int totalSpaces) {
        mPosition = new LatLng(lat, lng);
        mTitle = title;
        mSnippet = snippet;
        this.availableBikes = availableBikes;
        this.totalSpaces = totalSpaces;
    }

    @Override
    public LatLng getPosition() {
        return mPosition;
    }

    @Override
    public String getTitle() { return mTitle; }

    @Override
    public String getSnippet() { return mSnippet; }

    void setSnippet(String snippet) {
        mSnippet = snippet;
    }

    boolean isStartStation() {
        return isStartStation;
    }

    void setStartStation(boolean startStation) {
        isStartStation = startStation;
    }

    boolean isEndStation() {
        return isEndStation;
    }

    void setEndStation(boolean endStation) {
        isEndStation = endStation;
    }

    int getAvailableBikes() {
        return availableBikes;
    }

    int getTotalSpaces() {
        return totalSpaces;
    }

}
