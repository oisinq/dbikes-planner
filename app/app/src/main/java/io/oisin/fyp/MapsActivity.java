package io.oisin.fyp;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

import android.Manifest;
import android.content.pm.PackageManager;
import android.location.Location;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MapStyleOptions;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.maps.android.clustering.ClusterItem;
import com.google.maps.android.clustering.ClusterManager;
import com.google.maps.android.clustering.view.DefaultClusterRenderer;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

/**
 * This version of the map has clustering
 */
public class MapsActivity extends AppCompatActivity implements OnMapReadyCallback, ActivityCompat.OnRequestPermissionsResultCallback {

    private GoogleMap mMap;
    private ClusterManager<MyItem> mClusterManager;
    private static final int PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION = 1;
    private boolean mLocationPermissionGranted = false;
    private RequestQueue queue;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_maps);

        queue = Volley.newRequestQueue(this);

        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);

        Button refreshButton = findViewById(R.id.refresh_icon);
        refreshButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                makeApiRequest();
            }
        });
    }

    /**
     * Draws profile photos inside markers (using IconGenerator).
     * When there are multiple people in the cluster, draw multiple photos (using MultiDrawable).
     */
    private class StationRenderer extends DefaultClusterRenderer {

        public StationRenderer() {
            super(getApplicationContext(), getMap(), mClusterManager);
        }

        @Override
        protected void onBeforeClusterItemRendered(ClusterItem item, MarkerOptions markerOptions) {
            int availableBikes = Integer.parseInt(item.getSnippet().split(" bikes available")[0].split(" out of ")[0]);

            markerOptions.icon(BitmapDescriptorFactory.fromResource(getResourceForAvailableBikes(availableBikes)));

            super.onBeforeClusterItemRendered(item, markerOptions);
        }
    }


    private int getResourceForAvailableBikes(int availableBikes) {

        switch (availableBikes) {
            case 0:
                return R.drawable.zero_bikes_medium;
            case 1:
                return R.drawable.one_bike_medium;
            case 2:
                return R.drawable.two_bikes_medium;
            case 3:
                return R.drawable.three_bikes_medium;
            case 4:
                return R.drawable.four_bikes_medium;
            case 5:
                return R.drawable.five_bikes_medium;
            case 6:
                return R.drawable.six_bikes_medium;
            case 7:
                return R.drawable.seven_bikes_medium;
            case 8:
                return R.drawable.eight_bikes_medium;
            default:
                return R.drawable.nine_plus_bikes_medium;
        }
    }

    @Override
    public void onMapReady(final GoogleMap map) {
        mMap = map;
        mClusterManager = new ClusterManager<>(this, map);
        mClusterManager.setRenderer(new StationRenderer());
        map.setOnCameraIdleListener(mClusterManager);


        map.setMapStyle(new MapStyleOptions(getResources()
                .getString(R.string.map_style)));

        makeApiRequest();

        // Add a marker in Sydney and move the camera
        LatLng dublin = new LatLng(53.3498, -6.2603);
        map.moveCamera(CameraUpdateFactory.zoomTo(16f));
        map.moveCamera(CameraUpdateFactory.newLatLng(dublin));

        enableMyLocation();
    }
    /**
     * Enables the My Location layer if the fine location permission has been granted.
     */
    private void enableMyLocation() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED) {
            mMap.setMyLocationEnabled(true);
            mMap.getUiSettings().setMyLocationButtonEnabled(true);
            mMap.getUiSettings().setMapToolbarEnabled(false);
        } else {
            // Show rationale and request permission.
            ActivityCompat.requestPermissions(this,
                    new String[]{android.Manifest.permission.ACCESS_FINE_LOCATION},
                    PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION) {
            if (permissions.length == 1 &&
                    permissions[0].equals(Manifest.permission.ACCESS_FINE_LOCATION) &&
                    grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                mMap.setMyLocationEnabled(true);
                mMap.getUiSettings().setMyLocationButtonEnabled(true);
                mMap.getUiSettings().setMapToolbarEnabled(true);
            } else {
                // Permission was denied. Display an error message.
            }
        }
    }

    private void makeApiRequest() {
        String url = "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692";

        // Request a string response from the provided URL.
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        mMap.clear();
                        mClusterManager.clearItems();
                        
                        try {
                            JSONArray stations = new JSONArray(response);
                            List<MyItem> items = new ArrayList<>();

                            for (int i = 0; i < stations.length(); i++) {
                                JSONObject station = stations.getJSONObject(i);
                                items.add(new MyItem(station.getJSONObject("position").getDouble("lat"),
                                        station.getJSONObject("position").getDouble("lng"),
                                        station.getString("address"),
                                        station.getInt("available_bikes") + " out of " + station.getInt("bike_stands") + " bikes available"));
                            }

                            mClusterManager.addItems(items);
                            mClusterManager.cluster();
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
            }
        });

        queue.add(stringRequest);
    }


    public GoogleMap getMap() {
        return mMap;
    }
}
