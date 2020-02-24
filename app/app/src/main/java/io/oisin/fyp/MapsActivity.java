package io.oisin.fyp;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.formatter.ValueFormatter;
import com.github.mikephil.charting.utils.ColorTemplate;
import com.google.android.gms.maps.CameraUpdate;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.OnStreetViewPanoramaReadyCallback;
import com.google.android.gms.maps.StreetViewPanorama;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.SupportStreetViewPanoramaFragment;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MapStyleOptions;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.StreetViewPanoramaLocation;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import com.google.maps.android.clustering.ClusterItem;
import com.google.maps.android.clustering.ClusterManager;
import com.google.maps.android.clustering.view.DefaultClusterRenderer;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

/**
 * This version of the map has clustering
 */
public class MapsActivity extends AppCompatActivity implements OnMapReadyCallback, ActivityCompat.OnRequestPermissionsResultCallback, GoogleMap.OnMarkerClickListener {

    private GoogleMap mMap;
    private StreetViewPanorama mStreetViewPanorama;
    private ClusterManager<MyItem> mClusterManager;
    private static final int PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION = 1;
    private RequestQueue queue;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_maps);

        View bottomSheet = findViewById(R.id.bottom_sheet);
        BottomSheetBehavior bottomSheetBehavior = BottomSheetBehavior.from(bottomSheet);
        bottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN);

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

        SupportStreetViewPanoramaFragment streetViewPanoramaFragment =
                (SupportStreetViewPanoramaFragment)
                        getSupportFragmentManager().findFragmentById(R.id.streetviewpanorama);
        streetViewPanoramaFragment.getStreetViewPanoramaAsync(
                new OnStreetViewPanoramaReadyCallback() {
                    @Override
                    public void onStreetViewPanoramaReady(StreetViewPanorama panorama) {
                        mStreetViewPanorama = panorama;
                    }
                });

        setUpGraph();
    }

    private void setUpGraph() {
        LineChart chart = findViewById(R.id.availability_chart);
        chart.setBackgroundColor(Color.WHITE);

        XAxis xAxis = chart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.TOP_INSIDE);
        xAxis.setTextSize(10f);
        xAxis.setTextColor(Color.WHITE);
        xAxis.setDrawAxisLine(false);
        xAxis.setDrawGridLines(true);
        xAxis.setTextColor(Color.rgb(255, 192, 56));
        xAxis.setCenterAxisLabels(true);
        xAxis.setGranularity(1f); // one hour
        xAxis.setValueFormatter(new ValueFormatter() {

            private final SimpleDateFormat mFormat = new SimpleDateFormat("HH:mm", Locale.ENGLISH);

            @Override
            public String getFormattedValue(float value) {

                long millis = TimeUnit.HOURS.toMillis((long) value);
                return mFormat.format(new Date((long) value));
            }
        });

        YAxis leftAxis = chart.getAxisLeft();
        leftAxis.setPosition(YAxis.YAxisLabelPosition.INSIDE_CHART);
        leftAxis.setTextColor(ColorTemplate.getHoloBlue());
        leftAxis.setDrawGridLines(true);
        leftAxis.setGranularityEnabled(true);
        leftAxis.setYOffset(-9f);
        leftAxis.setTextColor(Color.rgb(255, 192, 56));

        YAxis rightAxis = chart.getAxisRight();
        rightAxis.setEnabled(false);

        ArrayList<Entry> values = new ArrayList<>();

        InputStream is = getResources().openRawResource(R.raw.bikes);
        BufferedReader reader = new BufferedReader(
                new InputStreamReader(is, Charset.forName("UTF-8")));
        String line = "";

        try {
            reader.readLine();
            while ((line = reader.readLine()) != null) {
                // Split the line into different tokens (using the comma as a separator).
                String[] tokens = line.split(",");

//                // Read the data and store it in the WellData POJO.
                DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.ENGLISH);
                values.add(new Entry((float) dateFormat.parse(tokens[4]).getTime(), Float.parseFloat(tokens[0])));

   //             values.add(new Entry(Float.parseFloat(tokens[1]), Float.parseFloat(tokens[0])));
            }
        } catch (Exception e1) {
            Log.e("MainActivity", "Error" + line, e1);
            e1.printStackTrace();
        }

        LineDataSet set1 = new LineDataSet(values, "Label");
        set1.setAxisDependency(YAxis.AxisDependency.LEFT);
        set1.setColor(ColorTemplate.getHoloBlue());
        set1.setValueTextColor(ColorTemplate.getHoloBlue());
        set1.setLineWidth(1.5f);
        set1.setDrawCircles(false);
        set1.setDrawValues(false);
        set1.setFillAlpha(65);
        set1.setFillColor(ColorTemplate.getHoloBlue());
        set1.setHighLightColor(Color.rgb(244, 117, 117));
        set1.setDrawCircleHole(false);
        set1.setMode(LineDataSet.Mode.CUBIC_BEZIER);

        LineData lineData = new LineData(set1);
        chart.setData(lineData);
        chart.invalidate();
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
        map.setOnMarkerClickListener(this);

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

    @Override
    public boolean onMarkerClick(final Marker marker) {
        if (marker.getTitle() == null) return false;

        View bottomSheet = findViewById(R.id.bottom_sheet);
        BottomSheetBehavior bottomSheetBehavior = BottomSheetBehavior.from(bottomSheet);

        TextView text = findViewById(R.id.bottom_sheet_title);
        text.setText(marker.getTitle());

        text = findViewById(R.id.bottom_sheet_byline);
        text.setText(marker.getSnippet());

        CameraUpdate yourLocation = CameraUpdateFactory.newLatLngZoom(marker.getPosition(), mMap.getCameraPosition().zoom);
        mMap.animateCamera(yourLocation, 300, null);

        mStreetViewPanorama.setPosition(marker.getPosition());

        bottomSheetBehavior.setState(BottomSheetBehavior.STATE_COLLAPSED);

        return true;
    }
}
