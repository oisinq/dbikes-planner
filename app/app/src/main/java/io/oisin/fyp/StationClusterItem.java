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

    public StationClusterItem(double lat, double lng, String title, String snippet, int availableBikes, int totalSpaces) {
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

    /**
     * Set the title of the marker
     * @param title string to be set as title
     */
    public void setTitle(String title) {
        mTitle = title;
    }

    /**
     * Set the description of the marker
     * @param snippet string to be set as snippet
     */
    public void setSnippet(String snippet) {
        mSnippet = snippet;
    }

    public boolean isStartStation() {
        return isStartStation;
    }

    public void setStartStation(boolean startStation) {
        isStartStation = startStation;
    }

    public boolean isEndStation() {
        return isEndStation;
    }

    public void setEndStation(boolean endStation) {
        isEndStation = endStation;
    }

    public int getAvailableBikes() {
        return availableBikes;
    }

    public void setAvailableBikes(int availableBikes) {
        this.availableBikes = availableBikes;
    }

    public int getTotalSpaces() {
        return totalSpaces;
    }

    public void setTotalSpaces(int totalSpaces) {
        this.totalSpaces = totalSpaces;
    }

}
