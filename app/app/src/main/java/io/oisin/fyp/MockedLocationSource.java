package io.oisin.fyp;

import android.location.Location;

import com.google.android.gms.maps.LocationSource;

/**
 * Created by Oisin Quinn (@oisin1001) on 16/04/2020.
 */
public class MockedLocationSource implements LocationSource {
    @Override
    public void activate(OnLocationChangedListener onLocationChangedListener) {
        Location mockedLocation = new Location("Dummy locator");
        mockedLocation.setLatitude(53.330667);
        mockedLocation.setLongitude(-6.258590);

        onLocationChangedListener.onLocationChanged(mockedLocation);
    }

    @Override
    public void deactivate() {

    }
}
